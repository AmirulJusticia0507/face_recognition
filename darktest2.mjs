export default async function run(page, ui) {
  await page.goto('http://localhost:5173/')
  await page.waitForTimeout(2000)

  const before = await page.evaluate(() => ({
    htmlClass: document.documentElement.className,
    bodyBg: getComputedStyle(document.body).backgroundColor
  }))

  const clicked = await page.evaluate(() => {
    const header = document.querySelector('header')
    if (!header) return 'no header'
    const buttons = header.querySelectorAll('button')
    for (const btn of buttons) {
      const label = btn.getAttribute('aria-label') || ''
      if (label.includes('dark') || label.includes('light') || label.includes('Switch')) {
        btn.click()
        return 'clicked: ' + label
      }
    }
    return 'buttons: ' + Array.from(buttons).map(b => b.getAttribute('aria-label')).join(', ')
  })

  await page.waitForTimeout(500)

  const afterClick = await page.evaluate(() => ({
    htmlClass: document.documentElement.className,
    bodyBg: getComputedStyle(document.body).backgroundColor,
    bodyColor: getComputedStyle(document.body).color,
    sidebarBg: (() => { const s = document.querySelector('aside'); return s ? getComputedStyle(s).backgroundColor : 'N/A' })(),
    headerBg: (() => { const h = document.querySelector('header'); return h ? getComputedStyle(h).backgroundColor : 'N/A' })()
  }))

  await page.screenshot({ path: 'C:/Users/amiru/AppData/Local/Temp/opencode/after-dark-toggle.png', fullPage: true })

  await page.evaluate(() => {
    const header = document.querySelector('header')
    if (!header) return
    const buttons = header.querySelectorAll('button')
    for (const btn of buttons) {
      const label = btn.getAttribute('aria-label') || ''
      if (label.includes('dark') || label.includes('light') || label.includes('Switch')) {
        btn.click()
        return
      }
    }
  })

  await page.waitForTimeout(500)
  await page.screenshot({ path: 'C:/Users/amiru/AppData/Local/Temp/opencode/after-light-toggle.png', fullPage: true })

  const afterBack = await page.evaluate(() => ({
    htmlClass: document.documentElement.className,
    bodyBg: getComputedStyle(document.body).backgroundColor
  }))

  return { before, clicked, afterClick, afterBack }
}