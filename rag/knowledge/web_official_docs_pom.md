# Playwright Docs — docs pom

Source: https://playwright.dev/docs/pom

Page object models | PlaywrightSkip to main contentOn this page
# Page object models

## Introduction​

Large test suites can be structured to optimize ease of authoring and maintenance. Page object models are one such approach to structure your test suite.

A page object represents a part of your web application. An e-commerce web application might have a home page, a listings page and a checkout page. Each of them can be represented by page object models.

Page objects simplify authoring by creating a higher-level API which suits your application and simplify maintenance by capturing element selectors in one place and create reusable code to avoid repetition.

## Implementation​

We will create a `PlaywrightDevPage` helper class to encapsulate common operations on the `playwright.dev` page. Internally, it will use the `page` object.

Test
Libraryplaywright-dev-page.ts
`import{ expect, type Locator, type Page}from'@playwright/test';

exportclassPlaywrightDevPage{
  readonly page:Page;
  readonly getStartedLink:Locator;
  readonly gettingStartedHeader:Locator;
  readonly pomLink:Locator;
  readonly tocList:Locator;

constructor(page:Page){
this.page= page;
this.getStartedLink= page.locator('a',{hasText:'Get started'});
this.gettingStartedHeader= page.locator('h1',{hasText:'Installation'});
this.pomLink= page.locator('li',{
hasText:'Guides',
}).locator('a',{
hasText:'Page Object Model',
});
this.tocList= page.locator('article div.markdown ul > li > a');
}

asyncgoto(){
awaitthis.page.goto('https://playwright.dev');
}

asyncgetStarted(){
awaitthis.getStartedLink.first().click();
awaitexpect(this.gettingStartedHeader).toBeVisible();
}

asyncpageObjectModel(){
awaitthis.getStarted();
awaitthis.pomLink.click();
}
}
`
models/PlaywrightDevPage.js
`classPlaywrightDevPage{
/**
   * @param{import('playwright').Page}page
   */
constructor(page){
this.page= page;
this.getStartedLink= page.locator('a',{hasText:'Get started'});
this.gettingStartedHeader= page.locator('h1',{hasText:'Installation'});
this.pomLink= page.locator('li',{
hasText:'Playwright Test',
}).locator('a',{
hasText:'Page Object Model',
});
this.tocList= page.locator('article div.markdown ul > li > a');
}
asyncgetStarted(){
awaitthis.getStartedLink.first().click();
awaitexpect(this.gettingStartedHeader).toBeVisible();
}

asyncpageObjectModel(){
awaitthis.getStarted();
awaitthis.pomLink.click();
}
}
module.exports={PlaywrightDevPage};
`

Now we can use the `PlaywrightDevPage` class in our tests.

Test
Libraryexample.spec.ts
`import{ test, expect }from'@playwright/test';
import{PlaywrightDevPage}from'./playwright-dev-page';

test('getting started should contain table of contents',async({ page })=>{
const playwrightDev =newPlaywrightDevPage(page);
await playwrightDev.goto();
await playwrightDev.getStarted();
awaitexpect(playwrightDev.tocList).toHaveText([
`How to install Playwright`,
`What's installed`,
`How to run the example test`,
`How to open the HTML test report`,
`Write tests using web-first assertions, fixtures and locators`,
`Run single or multiple tests; headed mode`,
`Generate tests with Codegen`,
`View a trace of your tests`,
]);
});

test('should show Page Object Model article',async({ page })=>{
const playwrightDev =newPlaywrightDevPage(page);
await playwrightDev.goto();
await playwrightDev.pageObjectModel();
awaitexpect(page.locator('article')).toContainText('Page Object Model is a common pattern');
});
`
example.spec.js
`const{PlaywrightDevPage}=require('./playwright-dev-page');

// In the test
const page =await browser.newPage();
await playwrightDev.goto();
await playwrightDev.getStarted();
awaitexpect(playwrightDev.tocList).toHaveText([
`How to install Playwright`,
`What's installed`,
`How to run the example test`,
`How to open the HTML test report`,
`Write tests using web-first assertions, fixtures and locators`,
`Run single or multiple tests; headed mode`,
`Generate tests with Codegen`,
`View a trace of your tests`,
]);
`

Introduction
Implementation
