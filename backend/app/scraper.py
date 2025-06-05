# scraper.py - Website Analysis and Content Extraction

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import base64
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Any, List, Optional
import logging
from urllib.parse import urljoin, urlparse
import time
from .utils import measure_performance, retry_async, setup_logging

logger = logging.getLogger(__name__)

class WebsiteScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    @retry_async(max_retries=3)
    @measure_performance
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website and extract all relevant content
        """
        logger.info(f"Starting to scrape website: {url}")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with optimized settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows'
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set additional headers
            await self.page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Navigate to the page with error handling
            try:
                response = await self.page.goto(
                    url, 
                    wait_until="networkidle", 
                    timeout=30000
                )
                
                if not response or response.status >= 400:
                    raise Exception(f"Failed to load page: HTTP {response.status if response else 'Unknown'}")
                
            except PlaywrightTimeoutError:
                logger.warning(f"Network idle timeout for {url}, trying with domcontentloaded")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Wait for page to settle
            await self.page.wait_for_timeout(3000)
            
            # Handle cookie banners and popups
            await self._handle_popups()
            
            # Get page content
            html_content = await self.page.content()
            
            # Extract structured data
            scraped_data = await self._extract_page_data(url, html_content)
            
            # Take screenshots at different viewport sizes
            screenshots = await self._capture_screenshots()
            scraped_data['screenshots'] = screenshots
            
            # Get performance metrics
            performance_data = await self._get_performance_metrics()
            scraped_data['performance'] = performance_data
            
            logger.info(f"Successfully scraped {url}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise Exception(f"Failed to scrape website: {str(e)}")
        finally:
            await self.cleanup()
    
    async def _handle_popups(self):
        """Handle common popups and cookie banners"""
        try:
            # Common cookie banner selectors
            popup_selectors = [
                '[id*="cookie"]', '[class*="cookie"]',
                '[id*="gdpr"]', '[class*="gdpr"]',
                '[id*="consent"]', '[class*="consent"]',
                '[id*="privacy"]', '[class*="privacy"]',
                '.modal', '.popup', '.overlay',
                '[role="dialog"]', '[role="alertdialog"]'
            ]
            
            for selector in popup_selectors:
                try:
                    # Check if popup exists
                    popup = await self.page.query_selector(selector)
                    if popup:
                        # Try to find and click accept/close buttons
                        close_buttons = await popup.query_selector_all(
                            'button:has-text("Accept"), button:has-text("Close"), button:has-text("OK"), '
                            'button:has-text("Agree"), button:has-text("Got it"), [aria-label="Close"], '
                            '.close, .dismiss, .accept'
                        )
                        
                        if close_buttons:
                            await close_buttons[0].click()
                            await self.page.wait_for_timeout(1000)
                            break
                except:
                    continue  # Try next selector
                    
        except Exception as e:
            logger.debug(f"Error handling popups: {e}")
    
    async def _capture_screenshots(self) -> Dict[str, str]:
        """Capture screenshots at different viewport sizes"""
        screenshots = {}
        
        try:
            viewport_sizes = [
                {'name': 'desktop', 'width': 1920, 'height': 1080},
                {'name': 'tablet', 'width': 768, 'height': 1024},
                {'name': 'mobile', 'width': 375, 'height': 667}
            ]
            
            for viewport in viewport_sizes:
                try:
                    await self.page.set_viewport_size({
                        'width': viewport['width'], 
                        'height': viewport['height']
                    })
                    await self.page.wait_for_timeout(1000)
                    
                    screenshot = await self.page.screenshot(full_page=True)
                    screenshots[viewport['name']] = base64.b64encode(screenshot).decode()
                    
                except Exception as e:
                    logger.warning(f"Failed to capture {viewport['name']} screenshot: {e}")
                    
        except Exception as e:
            logger.warning(f"Error capturing screenshots: {e}")
            
        return screenshots
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get page performance metrics"""
        try:
            metrics = await self.page.evaluate('''
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const paintEntries = performance.getEntriesByType('paint');
                    
                    return {
                        loadTime: perfData ? perfData.loadEventEnd - perfData.loadEventStart : 0,
                        domContentLoaded: perfData ? perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart : 0,
                        firstPaint: paintEntries.find(p => p.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paintEntries.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                        transferSize: perfData ? perfData.transferSize : 0,
                        encodedBodySize: perfData ? perfData.encodedBodySize : 0,
                        decodedBodySize: perfData ? perfData.decodedBodySize : 0
                    };
                }
            ''')
            return metrics
        except Exception as e:
            logger.warning(f"Error getting performance metrics: {e}")
            return {}
    
    async def _extract_page_data(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract structured data from HTML content"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Basic page information
        data = {
            'url': url,
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup),
            'meta_keywords': self._extract_meta_keywords(soup),
            'canonical_url': self._extract_canonical_url(soup),
            'language': self._extract_language(soup),
            'html_content': html_content,
            'text_content': self._extract_text_content(soup),
            'word_count': len(self._extract_text_content(soup).split()),
            'structure': await self._analyze_structure(soup),
            'styles': await self._extract_styles(soup),
            'scripts': self._extract_scripts(soup),
            'images': await self._extract_images(soup, url),
            'links': self._extract_links(soup, url),
            'forms': self._extract_forms(soup),
            'navigation': self._extract_navigation(soup),
            'layout': await self._analyze_layout(),
            'colors': self._extract_colors(soup),
            'fonts': self._extract_fonts(soup),
            'responsive_breakpoints': await self._detect_responsive_design(),
            'social_media': self._extract_social_media(soup),
            'structured_data': self._extract_structured_data(soup),
            'favicon': self._extract_favicon(soup, url),
            'analytics': self._extract_analytics(soup)
        }
        
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "Untitled"
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords.get('content', '').strip() if meta_keywords else ""
    
    def _extract_canonical_url(self, soup: BeautifulSoup) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href', '').strip() if canonical else ""
    
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Extract page language"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', '')
        
        return "en"  # Default to English
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    async def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the HTML structure"""
        structure = {
            'headings': [],
            'sections': [],
            'semantic_elements': [],
            'hierarchy': {},
            'content_blocks': []
        }
        
        # Extract headings with hierarchy
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for h in headings:
                structure['headings'].append({
                    'level': i,
                    'text': h.get_text().strip(),
                    'id': h.get('id'),
                    'class': h.get('class', []),
                    'position': len(structure['headings'])
                })
        
        # Extract semantic elements
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        for tag in semantic_tags:
            elements = soup.find_all(tag)
            for el in elements:
                structure['semantic_elements'].append({
                    'tag': tag,
                    'id': el.get('id'),
                    'class': el.get('class', []),
                    'text_preview': el.get_text()[:100].strip(),
                    'children_count': len(el.find_all())
                })
        
        # Extract major content blocks
        content_containers = soup.find_all(['div', 'section', 'article'], class_=True)
        for container in content_containers[:20]:  # Limit to first 20
            class_names = ' '.join(container.get('class', []))
            if any(keyword in class_names.lower() for keyword in ['content', 'main', 'body', 'article', 'post']):
                structure['content_blocks'].append({
                    'tag': container.name,
                    'classes': class_names,
                    'id': container.get('id', ''),
                    'text_length': len(container.get_text().strip()),
                    'child_count': len(container.find_all())
                })
        
        return structure
    
    async def _extract_styles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract CSS styles"""
        styles = {
            'inline_styles': [],
            'style_sheets': [],
            'external_css': [],
            'css_variables': [],
            'media_queries': []
        }
        
        # Extract inline styles
        elements_with_style = soup.find_all(style=True)
        styles['inline_styles'] = [el.get('style') for el in elements_with_style[:20]]  # Limit to first 20
        
        # Extract internal CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            styles['style_sheets'].append(css_content)
            
            # Extract CSS variables
            css_vars = re.findall(r'--[\w-]+:\s*[^;]+', css_content)
            styles['css_variables'].extend(css_vars)
            
            # Extract media queries
            media_queries = re.findall(r'@media[^{]+{[^}]*}', css_content, re.DOTALL)
            styles['media_queries'].extend(media_queries)
        
        # Extract external CSS links
        css_links = soup.find_all('link', rel='stylesheet')
        styles['external_css'] = [link.get('href') for link in css_links if link.get('href')]
        
        return styles
    
    def _extract_scripts(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract JavaScript references and inline scripts"""
        scripts = {
            'external': [],
            'inline': [],
            'frameworks_detected': []
        }
        
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if script.get('src'):
                src = script.get('src')
                scripts['external'].append(src)
                
                # Detect common frameworks
                if any(framework in src.lower() for framework in ['react', 'vue', 'angular', 'jquery']):
                    framework_name = next(fw for fw in ['react', 'vue', 'angular', 'jquery'] if fw in src.lower())
                    if framework_name not in scripts['frameworks_detected']:
                        scripts['frameworks_detected'].append(framework_name)
                        
            elif script.string:
                # Include inline scripts (first 200 chars)
                inline_content = script.string[:200].strip()
                if inline_content:
                    scripts['inline'].append(inline_content)
        
        return scripts
    
    async def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract image information"""
        images = []
        img_tags = soup.find_all('img')
        
        for img in img_tags[:30]:  # Limit to first 30 images
            src = img.get('src', '')
            if src:
                # Make absolute URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                elif not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'class': ' '.join(img.get('class', [])),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', ''),
                'sizes': img.get('sizes', ''),
                'data_src': img.get('data-src', ''),  # Lazy loading
                'is_decorative': not img.get('alt', '').strip()
            })
        
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[Dict[str, str]]]:
        """Extract link information categorized by type"""
        links = {
            'internal': [],
            'external': [],
            'email': [],
            'phone': [],
            'download': []
        }
        
        a_tags = soup.find_all('a', href=True)
        base_domain = urlparse(base_url).netloc
        
        for link in a_tags[:100]:  # Limit to first 100 links
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            
            if not href:
                continue
            
            link_data = {
                'href': href,
                'text': text,
                'title': link.get('title', ''),
                'target': link.get('target', ''),
                'class': ' '.join(link.get('class', [])),
                'rel': ' '.join(link.get('rel', []))
            }
            
            # Categorize links
            if href.startswith('mailto:'):
                links['email'].append(link_data)
            elif href.startswith('tel:'):
                links['phone'].append(link_data)
            elif any(ext in href.lower() for ext in ['.pdf', '.doc', '.zip', '.mp3', '.mp4']):
                links['download'].append(link_data)
            elif href.startswith(('http://', 'https://')):
                if base_domain in href:
                    links['internal'].append(link_data)
                else:
                    links['external'].append(link_data)
            else:
                links['internal'].append(link_data)
        
        return links
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        form_tags = soup.find_all('form')
        
        for form in form_tags:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'enctype': form.get('enctype', ''),
                'id': form.get('id', ''),
                'class': ' '.join(form.get('class', [])),
                'fields': [],
                'buttons': []
            }
            
            # Extract form fields
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_field in inputs:
                field_data = {
                    'tag': input_field.name,
                    'type': input_field.get('type', ''),
                    'name': input_field.get('name', ''),
                    'id': input_field.get('id', ''),
                    'placeholder': input_field.get('placeholder', ''),
                    'required': input_field.has_attr('required'),
                    'class': ' '.join(input_field.get('class', [])),
                    'value': input_field.get('value', '')
                }
                
                # Special handling for select elements
                if input_field.name == 'select':
                    options = input_field.find_all('option')
                    field_data['options'] = [
                        {'value': opt.get('value', ''), 'text': opt.get_text().strip()}
                        for opt in options
                    ]
                
                form_data['fields'].append(field_data)
            
            # Extract buttons
            buttons = form.find_all(['button', 'input[type="submit"]', 'input[type="button"]'])
            for button in buttons:
                button_data = {
                    'tag': button.name,
                    'type': button.get('type', ''),
                    'text': button.get_text().strip() or button.get('value', ''),
                    'class': ' '.join(button.get('class', []))
                }
                form_data['buttons'].append(button_data)
            
            forms.append(form_data)
        
        return forms
    
    def _extract_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract navigation structure"""
        nav_data = {
            'nav_elements': [],
            'breadcrumbs': [],
            'menu_structure': []
        }
        
        # Find navigation elements
        nav_tags = soup.find_all('nav')
        for nav in nav_tags:
            nav_info = {
                'class': ' '.join(nav.get('class', [])),
                'id': nav.get('id', ''),
                'role': nav.get('role', ''),
                'links': [],
                'sublists': []
            }
            
            # Extract links within nav
            nav_links = nav.find_all('a')
            for link in nav_links:
                nav_info['links'].append({
                    'href': link.get('href', ''),
                    'text': link.get_text().strip(),
                    'class': ' '.join(link.get('class', []))
                })
            
            # Extract nested lists (dropdowns/submenus)
            sublists = nav.find_all('ul')
            nav_info['sublists'] = len(sublists)
            
            nav_data['nav_elements'].append(nav_info)
        
        # Look for breadcrumbs
        breadcrumb_selectors = [
            '[class*="breadcrumb"]',
            '[id*="breadcrumb"]',
            'nav ol',
            '.breadcrumbs'
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumbs = soup.select(selector)
            for bc in breadcrumbs:
                links = bc.find_all('a')
                if links:
                    nav_data['breadcrumbs'].append([
                        {'text': link.get_text().strip(), 'href': link.get('href', '')}
                        for link in links
                    ])
        
        return nav_data
    
    async def _analyze_layout(self) -> Dict[str, Any]:
        """Analyze the page layout using Playwright"""
        if not self.page:
            return {}
        
        try:
            # Get layout information
            layout_info = await self.page.evaluate('''
                () => {
                    const containers = document.querySelectorAll('div, section, main, header, footer, article, aside');
                    const layout = [];
                    
                    for (let i = 0; i < Math.min(containers.length, 30); i++) {
                        const container = containers[i];
                        const rect = container.getBoundingClientRect();
                        const styles = window.getComputedStyle(container);
                        
                        // Only include visible elements
                        if (rect.width > 0 && rect.height > 0) {
                            layout.push({
                                tagName: container.tagName,
                                className: container.className,
                                id: container.id,
                                position: {
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                },
                                styles: {
                                    display: styles.display,
                                    position: styles.position,
                                    zIndex: styles.zIndex,
                                    flexDirection: styles.flexDirection,
                                    gridTemplateColumns: styles.gridTemplateColumns,
                                    backgroundColor: styles.backgroundColor,
                                    padding: styles.padding,
                                    margin: styles.margin
                                }
                            });
                        }
                    }
                    
                    return {
                        viewport: { 
                            width: window.innerWidth, 
                            height: window.innerHeight 
                        },
                        containers: layout,
                        bodyStyles: {
                            fontFamily: window.getComputedStyle(document.body).fontFamily,
                            fontSize: window.getComputedStyle(document.body).fontSize,
                            backgroundColor: window.getComputedStyle(document.body).backgroundColor,
                            color: window.getComputedStyle(document.body).color
                        }
                    };
                }
            ''')
            
            return layout_info
        except Exception as e:
            logger.warning(f"Error analyzing layout: {e}")
            return {}
    
    def _extract_colors(self, soup: BeautifulSoup) -> List[str]:
        """Extract color palette from styles"""
        colors = set()
        
        # Extract from inline styles
        elements_with_style = soup.find_all(style=True)
        for el in elements_with_style:
            style = el.get('style', '')
            # Extract hex colors
            hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', style)
            colors.update(hex_colors)
            # Extract rgb colors
            rgb_colors = re.findall(r'rgb\([^)]+\)', style)
            colors.update(rgb_colors)
        
        # Extract from CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', css_content)
            colors.update(hex_colors)
            rgb_colors = re.findall(r'rgb\([^)]+\)', css_content)
            colors.update(rgb_colors)
        
        return list(colors)[:30]  # Limit to 30 colors
    
    def _extract_fonts(self, soup: BeautifulSoup) -> List[str]:
        """Extract font families used"""
        fonts = set()
        
        # Extract from inline styles
        elements_with_style = soup.find_all(style=True)
        for el in elements_with_style:
            style = el.get('style', '')
            if 'font-family' in style:
                font_match = re.search(r'font-family:\s*([^;]+)', style, re.IGNORECASE)
                if font_match:
                    font_family = font_match.group(1).strip().replace('"', "'")
                    fonts.add(font_family)
        
        # Extract from CSS
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            font_matches = re.findall(r'font-family:\s*([^;]+)', css_content, re.IGNORECASE)
            for font_match in font_matches:
                font_family = font_match.strip().replace('"', "'")
                fonts.add(font_family)
        
        return list(fonts)[:15]  # Limit to 15 fonts
    
    async def _detect_responsive_design(self) -> Dict[str, Any]:
        """Detect responsive design patterns"""
        if not self.page:
            return {}
        
        try:
            # Check for viewport meta tag
            viewport_meta = await self.page.evaluate('''
                () => {
                    const meta = document.querySelector('meta[name="viewport"]');
                    return meta ? meta.getAttribute('content') : null;
                }
            ''')
            
            # Test different viewport sizes
            breakpoints = []
            test_widths = [320, 768, 1024, 1440]
            
            for width in test_widths:
                try:
                    await self.page.set_viewport_size({"width": width, "height": 800})
                    await self.page.wait_for_timeout(500)
                    
                    # Check if layout changes
                    layout_info = await self.page.evaluate(f'''
                        () => {{
                            const body = document.body;
                            const computedStyle = window.getComputedStyle(body);
                            const container = document.querySelector('main, .container, .wrapper, .content') || body;
                            const containerStyle = window.getComputedStyle(container);
                            
                            return {{
                                width: {width},
                                bodyWidth: body.offsetWidth,
                                fontSize: computedStyle.fontSize,
                                containerMaxWidth: containerStyle.maxWidth,
                                containerPadding: containerStyle.padding,
                                gridColumns: containerStyle.gridTemplateColumns,
                                flexDirection: containerStyle.flexDirection
                            }};
                        }}
                    ''')
                    
                    breakpoints.append(layout_info)
                except Exception as e:
                    logger.warning(f"Error testing viewport {width}: {e}")
            
            return {
                'viewport_meta': viewport_meta,
                'breakpoint_tests': breakpoints,
                'is_responsive': viewport_meta is not None and 'width=device-width' in (viewport_meta or ''),
                'has_media_queries': len(breakpoints) > 1 and any(
                    bp['containerMaxWidth'] != breakpoints[0]['containerMaxWidth'] 
                    for bp in breakpoints[1:]
                )
            }
        except Exception as e:
            logger.warning(f"Error detecting responsive design: {e}")
            return {'is_responsive': False}
    
    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract social media information"""
        social_data = {
            'og_tags': {},
            'twitter_cards': {},
            'social_links': []
        }
        
        # Extract Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                social_data['og_tags'][property_name] = content
        
        # Extract Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                social_data['twitter_cards'][name] = content
        
        # Extract social media links
        social_platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'pinterest']
        social_links = soup.find_all('a', href=True)
        
        for link in social_links:
            href = link.get('href', '').lower()
            for platform in social_platforms:
                if platform in href:
                    social_data['social_links'].append({
                        'platform': platform,
                        'url': link.get('href'),
                        'text': link.get_text().strip(),
                        'class': ' '.join(link.get('class', []))
                    })
                    break
        
        return social_data
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata)"""
        structured_data = []
        
        # Extract JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Extract microdata
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        for element in microdata_elements[:10]:  # Limit to first 10
            item_data = {
                'type': 'microdata',
                'itemtype': element.get('itemtype', ''),
                'properties': {}
            }
            
            # Find properties within this scope
            props = element.find_all(attrs={'itemprop': True})
            for prop in props:
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.get_text().strip()
                item_data['properties'][prop_name] = prop_value
            
            if item_data['properties']:
                structured_data.append(item_data)
        
        return structured_data
    
    def _extract_favicon(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract favicon information"""
        favicon_data = {}
        
        # Common favicon selectors
        favicon_selectors = [
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
            'link[rel="apple-touch-icon"]',
            'link[rel="apple-touch-icon-precomposed"]'
        ]
        
        for selector in favicon_selectors:
            favicon = soup.select_one(selector)
            if favicon and favicon.get('href'):
                href = favicon.get('href')
                
                # Make absolute URL
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                rel = favicon.get('rel', 'icon')
                favicon_data[rel] = {
                    'href': href,
                    'sizes': favicon.get('sizes', ''),
                    'type': favicon.get('type', '')
                }
        
        # Default favicon location
        if not favicon_data:
            favicon_data['icon'] = {
                'href': urljoin(base_url, '/favicon.ico'),
                'sizes': '',
                'type': 'image/x-icon'
            }
        
        return favicon_data
    
    def _extract_analytics(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract analytics and tracking information"""
        analytics = {
            'google_analytics': [],
            'google_tag_manager': [],
            'facebook_pixel': [],
            'other_tracking': []
        }
        
        # Look in script tags for tracking codes
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.get_text().lower()
            src = script.get('src', '').lower()
            
            # Google Analytics
            if 'google-analytics.com' in src or 'gtag(' in script_content or 'ga(' in script_content:
                # Extract GA tracking ID
                ga_matches = re.findall(r'["\']UA-\d+-\d+["\']', script_content)
                ga_matches.extend(re.findall(r'["\']G-[A-Z0-9]+["\']', script_content))
                analytics['google_analytics'].extend([match.strip('"\'') for match in ga_matches])
            
            # Google Tag Manager
            if 'googletagmanager.com' in src or 'gtm-' in script_content:
                gtm_matches = re.findall(r'["\']GTM-[A-Z0-9]+["\']', script_content)
                analytics['google_tag_manager'].extend([match.strip('"\'') for match in gtm_matches])
            
            # Facebook Pixel
            if 'connect.facebook.net' in src or 'fbq(' in script_content:
                fb_matches = re.findall(r'fbq\(["\']init["\'],\s*["\'](\d+)["\']', script_content)
                analytics['facebook_pixel'].extend(fb_matches)
            
            # Other tracking services
            tracking_domains = ['hotjar', 'mixpanel', 'segment', 'amplitude', 'intercom']
            for domain in tracking_domains:
                if domain in src or domain in script_content:
                    analytics['other_tracking'].append(domain)
        
        # Remove duplicates
        for key in analytics:
            analytics[key] = list(set(analytics[key]))
        
        return analytics
    
    async def scrape_multiple_pages(self, urls: List[str], max_concurrent: int = 3) -> Dict[str, Dict[str, Any]]:
        """Scrape multiple pages concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single(url: str) -> tuple[str, Dict[str, Any]]:
            async with semaphore:
                try:
                    result = await self.scrape_website(url)
                    return url, result
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return url, {'error': str(e)}
        
        # Execute scraping tasks concurrently
        tasks = [scrape_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results
        scraped_data = {}
        for result in results:
            if isinstance(result, tuple):
                url, data = result
                scraped_data[url] = data
            else:
                logger.error(f"Unexpected result type: {type(result)}")
        
        return scraped_data
    
    async def get_page_insights(self, url: str) -> Dict[str, Any]:
        """Get additional page insights using Playwright"""
        if not self.page:
            raise Exception("Page not initialized. Call scrape_website first.")
        
        try:
            insights = await self.page.evaluate('''
                () => {
                    const insights = {};
                    
                    // Count elements
                    insights.elementCounts = {
                        total: document.querySelectorAll('*').length,
                        divs: document.querySelectorAll('div').length,
                        images: document.querySelectorAll('img').length,
                        links: document.querySelectorAll('a').length,
                        forms: document.querySelectorAll('form').length,
                        inputs: document.querySelectorAll('input').length,
                        buttons: document.querySelectorAll('button').length
                    };
                    
                    // Check for common libraries/frameworks
                    insights.librariesDetected = [];
                    if (window.jQuery) insights.librariesDetected.push('jQuery');
                    if (window.React) insights.librariesDetected.push('React');
                    if (window.Vue) insights.librariesDetected.push('Vue');
                    if (window.angular) insights.librariesDetected.push('Angular');
                    if (window.bootstrap) insights.librariesDetected.push('Bootstrap');
                    
                    // Page load state
                    insights.loadState = {
                        readyState: document.readyState,
                        hidden: document.hidden,
                        visibilityState: document.visibilityState
                    };
                    
                    // Viewport and scroll info
                    insights.viewport = {
                        width: window.innerWidth,
                        height: window.innerHeight,
                        scrollHeight: document.documentElement.scrollHeight,
                        scrollTop: window.pageYOffset || document.documentElement.scrollTop
                    };
                    
                    return insights;
                }
            ''')
            
            return insights
            
        except Exception as e:
            logger.warning(f"Error getting page insights: {e}")
            return {}
    
    def get_scraping_summary(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the scraped data"""
        summary = {
            'url': scraped_data.get('url', ''),
            'title': scraped_data.get('title', ''),
            'word_count': scraped_data.get('word_count', 0),
            'image_count': len(scraped_data.get('images', [])),
            'link_count': sum(len(links) for links in scraped_data.get('links', {}).values()),
            'form_count': len(scraped_data.get('forms', [])),
            'heading_count': len(scraped_data.get('structure', {}).get('headings', [])),
            'color_count': len(scraped_data.get('colors', [])),
            'font_count': len(scraped_data.get('fonts', [])),
            'has_responsive_design': scraped_data.get('responsive_breakpoints', {}).get('is_responsive', False),
            'has_social_media': bool(scraped_data.get('social_media', {}).get('social_links', [])),
            'has_analytics': any(scraped_data.get('analytics', {}).values()),
            'performance_score': self._calculate_performance_score(scraped_data),
            'complexity_score': self._calculate_complexity_score(scraped_data)
        }
        
        return summary
    
    def _calculate_performance_score(self, scraped_data: Dict[str, Any]) -> float:
        """Calculate a simple performance score (0-100)"""
        score = 100.0
        
        # Deduct points for large numbers of elements
        image_count = len(scraped_data.get('images', []))
        if image_count > 50:
            score -= min(20, (image_count - 50) * 0.5)
        
        # Deduct points for external scripts
        external_scripts = len(scraped_data.get('scripts', {}).get('external', []))
        if external_scripts > 10:
            score -= min(15, (external_scripts - 10) * 1.5)
        
        # Deduct points for large CSS files
        css_count = len(scraped_data.get('styles', {}).get('external_css', []))
        if css_count > 5:
            score -= min(10, (css_count - 5) * 2)
        
        return max(0, score)
    
    def _calculate_complexity_score(self, scraped_data: Dict[str, Any]) -> float:
        """Calculate a website complexity score (0-100)"""
        score = 0
        
        # Add points for various elements
        score += min(20, len(scraped_data.get('structure', {}).get('headings', [])) * 2)
        score += min(15, len(scraped_data.get('forms', [])) * 5)
        score += min(10, len(scraped_data.get('images', [])) * 0.2)
        score += min(15, len(scraped_data.get('scripts', {}).get('external', [])) * 1.5)
        score += min(10, len(scraped_data.get('styles', {}).get('external_css', [])) * 2)
        
        # Add points for advanced features
        if scraped_data.get('responsive_breakpoints', {}).get('is_responsive'):
            score += 10
        if scraped_data.get('social_media', {}).get('social_links'):
            score += 5
        if any(scraped_data.get('analytics', {}).values()):
            score += 5
        if scraped_data.get('structured_data'):
            score += 10
        
        return min(100, score)