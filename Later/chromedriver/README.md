# ChromeDriver

### ChromeDriver is an implementation of the WebDriver standard, which allows users to automate testing of their website across browsers.

## Please download the relevant ChromeDriver for your operating system

Both GoogleChrome and Chromedriver are required for the LaterChromeDriver() class to be implemented.
The chromedriver.exe file avaliable in the directory is the 91.0.4472.101 version for Windows.
If your installed GoogleChrome is a verseion > 91 and/or your operating system is not windows please install the relevant chromedriver for your system

To install ChromeDriver follow the instructions on either of these two sources: 
    https://chromedriver.chromium.org/downloads
    https://github.com/jsakamoto/nupkg-selenium-webdriver-chromedriver

## Architecture

ChromeDriver is shipped separately from Chrome. It controls Chrome out of
process through DevTools (WebKit Inspector). ChromeDriver is a shared library
which exports a few functions for executing WebDriver-standard commands, which
are packaged in JSON. For internal use, a custom python client for ChromeDriver
is available in chromedriver.py, which works on desktop (win/mac/linux) with
the shared library ChromeDriver.

The ChromeDriver shared library runs commands on the same thread that calls
ExecuteCommand. It doesn't create any additional threads except for the IO
thread. The IO thread is used to keep reading incoming data from Chrome in the
background.

ChromeDriver is also available as a standalone server executable which
communicates via the WebDriver JSON wire protocol. This can be used with the
open source WebDriver client libraries.