import express from 'express'
import cors from 'cors'
import crypto from 'crypto'
import { MongoClient } from 'mongodb'

const app = express()
const PORT = 3007
const MONGO_URL = 'mongodb://r2d2-mongodb:27017'
const DB_NAME = 'analytics'

app.use(cors({ origin: '*' }))
app.use(express.json())

let db

async function connect() {
  const client = new MongoClient(MONGO_URL)
  await client.connect()
  db = client.db(DB_NAME)
  await db.collection('visits').createIndex({ site: 1, ipHash: 1, day: 1 }, { unique: true })
  await db.collection('visits').createIndex({ site: 1 })
  await db.collection('visits').createIndex({ ts: 1 })
  await db.collection('visits').createIndex({ site: 1, day: 1 })
  console.log('✅ Connected to MongoDB')
}

// Parse browser + device from User-Agent string
function parseUserAgent(ua = '') {
  const s = ua.toLowerCase()

  // Browser
  let browser = 'Other'
  if (s.includes('edg/') || s.includes('edge/'))        browser = 'Edge'
  else if (s.includes('opr/') || s.includes('opera'))    browser = 'Opera'
  else if (s.includes('chrome') && !s.includes('chromium')) browser = 'Chrome'
  else if (s.includes('chromium'))                        browser = 'Chromium'
  else if (s.includes('firefox') || s.includes('fxios')) browser = 'Firefox'
  else if (s.includes('safari') && !s.includes('chrome')) browser = 'Safari'
  else if (s.includes('samsungbrowser'))                  browser = 'Samsung Browser'
  else if (s.includes('duckduckgo'))                      browser = 'DuckDuckGo'

  // Device type
  let device = 'Desktop'
  if (/(tablet|ipad|playbook|silk)/.test(s))             device = 'Tablet'
  else if (/(mobile|iphone|ipod|android|blackberry|mini|windows\sce|palm)/.test(s)) device = 'Mobile'

  // OS
  let os = 'Other'
  if (s.includes('windows'))      os = 'Windows'
  else if (s.includes('android')) os = 'Android'
  else if (s.includes('iphone') || s.includes('ipad') || s.includes('ipod')) os = 'iOS'
  else if (s.includes('mac os'))  os = 'macOS'
  else if (s.includes('linux'))   os = 'Linux'

  return { browser, device, os }
}

// Track a visit — deduplicated by IP + site + day
app.post('/track', async (req, res) => {
  try {
    const { site } = req.body
    if (!site) return res.status(400).json({ error: 'site required' })

    const ip = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.ip || 'unknown'
    const ipHash = crypto.createHash('sha256').update(ip + (process.env.HASH_SALT || 'r2d2salt')).digest('hex')
    const now = new Date()
    const day = now.toISOString().slice(0, 10) // YYYY-MM-DD

    const ua = req.headers['user-agent'] || ''
    const { browser, device, os } = parseUserAgent(ua)

    // Referrer (optional, sent from frontend)
    const referrer = req.body.referrer || req.headers['referer'] || null

    const doc = {
      site,
      ipHash,
      day,
      ts: now,
      // Time breakdown for analytics queries
      hour: now.getUTCHours(),
      dayOfWeek: now.getUTCDay(), // 0=Sun ... 6=Sat
      month: now.getUTCMonth() + 1,
      year: now.getUTCFullYear(),
      // Device info
      browser,
      device,
      os,
      // Optional
      ...(referrer ? { referrer } : {}),
    }

    try {
      await db.collection('visits').insertOne(doc)
    } catch (e) {
      if (e.code !== 11000) throw e
      // Same IP today — update device info in case they switched browser
    }

    res.json({ ok: true })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'internal error' })
  }
})

// Total unique visitor count for a site
app.get('/count/:site', async (req, res) => {
  try {
    const { site } = req.params
    const total = await db.collection('visits').countDocuments({ site })
    res.json({ site, count: total })
  } catch (err) {
    res.status(500).json({ error: 'internal error' })
  }
})

// Counts for all sites
app.get('/counts', async (req, res) => {
  try {
    const sites = ['portfolio', 'lab', 'headlines']
    const results = {}
    for (const site of sites) {
      results[site] = await db.collection('visits').countDocuments({ site })
    }
    res.json(results)
  } catch (err) {
    res.status(500).json({ error: 'internal error' })
  }
})

// Stats breakdown for a site: by browser, device, OS, daily, hourly
app.get('/stats/:site', async (req, res) => {
  try {
    const { site } = req.params

    const [byBrowser, byDevice, byOS, byDay] = await Promise.all([
      db.collection('visits').aggregate([
        { $match: { site } },
        { $group: { _id: '$browser', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
      ]).toArray(),

      db.collection('visits').aggregate([
        { $match: { site } },
        { $group: { _id: '$device', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
      ]).toArray(),

      db.collection('visits').aggregate([
        { $match: { site } },
        { $group: { _id: '$os', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
      ]).toArray(),

      db.collection('visits').aggregate([
        { $match: { site } },
        { $group: { _id: '$day', count: { $sum: 1 } } },
        { $sort: { _id: -1 } },
        { $limit: 30 },
      ]).toArray(),
    ])

    const total = await db.collection('visits').countDocuments({ site })

    res.json({
      site,
      total,
      byBrowser:  byBrowser.map(d => ({ name: d._id, count: d.count })),
      byDevice:   byDevice.map(d => ({ name: d._id, count: d.count })),
      byOS:       byOS.map(d => ({ name: d._id, count: d.count })),
      byDay:      byDay.map(d => ({ date: d._id, count: d.count })),
    })
  } catch (err) {
    res.status(500).json({ error: 'internal error' })
  }
})

// All sites summary
app.get('/stats', async (req, res) => {
  try {
    const sites = ['portfolio', 'lab', 'headlines']
    const summary = {}
    for (const site of sites) {
      const total = await db.collection('visits').countDocuments({ site })
      const today = new Date().toISOString().slice(0, 10)
      const todayCount = await db.collection('visits').countDocuments({ site, day: today })
      summary[site] = { total, today: todayCount }
    }
    res.json(summary)
  } catch (err) {
    res.status(500).json({ error: 'internal error' })
  }
})

// Health check
app.get('/health', (_, res) => res.json({ ok: true, ts: new Date() }))

connect().then(() => {
  app.listen(PORT, () => console.log(`📊 Analytics API running on :${PORT}`))
}).catch(err => {
  console.error('Failed to connect to MongoDB:', err)
  process.exit(1)
})
