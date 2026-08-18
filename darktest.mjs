export default async function run(page, ui) {
  await page.screenshot({ path: 'C:/Users/amiru/AppData/Local/Temp/opencode/light-mode.png', fullPage: true })

  await page.evaluate(() => {
    document.documentElement.classList.add('dark')
  })
  await page.waitForTimeout(500)
  
  const stylesAfter = await page.evaluate(() => {
    const body = document.body
    const bodyBg = getComputedStyle(body).backgroundColor
    const bodyColor = getComputedStyle(body).color
    const sidebar = document.querySelector('aside')
    const sidebarBg = sidebar ? getComputedStyle(sidebar).backgroundColor : 'no sidebar'
    const cards = document.querySelectorAll('[class*="bg-white"]')
    const cardBgs = Array.from(cards).slice(0, 3).map(c => getComputedStyle(c).backgroundColor)
    return { bodyBg, bodyColor, sidebarBg, cardBgs, htmlClass: document.documentElement.className }
  })

  await page.screenshot({ path: 'C:/Users/amiru/AppData/Local/Temp/opencode/dark-mode.png', fullPage: true })

  await page.evaluate(() => {
    document.documentElement.classList.remove('dark')
  })
  await page.waitForTimeout(300)

  const stylesBack = await page.evaluate(() => {
    return {
      bodyBg: getComputedStyle(document.body).backgroundColor,
      htmlClass: document.documentElement.className
    }
  })

  return { stylesAfter, stylesBack }
}