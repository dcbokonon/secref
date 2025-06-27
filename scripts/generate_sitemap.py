#!/usr/bin/env python3
"""
SecRef Sitemap Generator

Dynamically generates sitemap.xml based on actual content
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SitemapGenerator:
    """Generate sitemap.xml from content"""

    def __init__(self, base_url="https://secref.org"):
        self.base_url = base_url.rstrip("/")
        self.project_root = Path(__file__).parent.parent

    def prettify(self, elem):
        """Return a pretty-printed XML string"""
        rough_string = tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def create_url_element(self, loc, lastmod=None, changefreq=None, priority=None):
        """Create a URL element"""
        url = Element("url")
        
        loc_elem = SubElement(url, "loc")
        loc_elem.text = loc
        
        if lastmod:
            lastmod_elem = SubElement(url, "lastmod")
            lastmod_elem.text = lastmod
        
        if changefreq:
            changefreq_elem = SubElement(url, "changefreq")
            changefreq_elem.text = changefreq
        
        if priority is not None:
            priority_elem = SubElement(url, "priority")
            priority_elem.text = str(priority)
        
        return url

    def get_json_files(self):
        """Find all JSON data files"""
        data_dir = self.project_root / "src" / "data"
        if data_dir.exists():
            return list(data_dir.glob("**/*.json"))
        return []

    def get_categories_from_json(self):
        """Extract categories from JSON files"""
        categories = set()
        
        for json_file in self.get_json_files():
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    
                # Extract categories from the data structure
                if isinstance(data, dict):
                    for category in data.keys():
                        categories.add(category)
                        if isinstance(data[category], dict):
                            for subcategory in data[category].keys():
                                categories.add(f"{category}/{subcategory}")
                                
            except (json.JSONDecodeError, KeyError):
                continue
        
        return sorted(categories)

    def generate_sitemap(self):
        """Generate the complete sitemap"""
        urlset = Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Static pages with priorities
        static_pages = [
            ("/", "daily", 1.0),
            ("/tools", "daily", 0.9),
            ("/learn", "weekly", 0.8),
            ("/events", "daily", 0.8),
            ("/groups", "weekly", 0.8),
            ("/about", "monthly", 0.5),
            ("/contributing", "monthly", 0.5),
            ("/privacy", "yearly", 0.3),
            ("/terms", "yearly", 0.3),
        ]
        
        # Add static pages
        for path, freq, priority in static_pages:
            url = self.create_url_element(
                f"{self.base_url}{path}",
                lastmod=today,
                changefreq=freq,
                priority=priority
            )
            urlset.append(url)
        
        # Add dynamic category pages
        categories = self.get_categories_from_json()
        for category in categories:
            # Skip if it's a subcategory (contains /)
            if "/" in category:
                continue
                
            url_path = f"/tools/{category.lower().replace(' ', '-')}"
            url = self.create_url_element(
                f"{self.base_url}{url_path}",
                lastmod=today,
                changefreq="weekly",
                priority=0.7
            )
            urlset.append(url)
        
        # Tool subcategories
        tool_categories = [
            "reconnaissance/network-discovery",
            "reconnaissance/osint",
            "vulnerability-assessment/scanners",
            "vulnerability-assessment/configuration",
            "exploitation/frameworks",
            "exploitation/post-exploitation",
            "exploitation/platform-specific",
            "defense-monitoring/network-defense",
            "defense-monitoring/security-monitoring",
            "defense-monitoring/threat-intelligence",
            "forensics/digital-forensics",
            "forensics/incident-response",
            "cryptography/tools",
            "cryptography/privacy",
            "binary-analysis/static",
            "binary-analysis/dynamic",
            "development-security/code-analysis",
            "development-security/devsecops",
            "physical-hardware/hardware-hacking",
            "physical-hardware/physical-security",
        ]
        
        for category in tool_categories:
            url = self.create_url_element(
                f"{self.base_url}/tools/{category}",
                lastmod=today,
                changefreq="weekly",
                priority=0.6
            )
            urlset.append(url)
        
        # Learning subcategories
        learning_categories = [
            "certifications/entry-level",
            "certifications/offensive",
            "certifications/defensive",
            "certifications/management",
            "certifications/specialized",
            "training-platforms/hands-on",
            "training-platforms/ctf",
            "training-platforms/video",
            "documentation/guides",
            "documentation/references",
            "documentation/standards",
            "practice/vulnerable-apps",
            "practice/challenges",
            "practice/labs",
            "career/job-boards",
            "career/interview",
            "career/paths",
            "career/salary",
        ]
        
        for category in learning_categories:
            url = self.create_url_element(
                f"{self.base_url}/learn/{category}",
                lastmod=today,
                changefreq="weekly",
                priority=0.6
            )
            urlset.append(url)
        
        return self.prettify(urlset)

    def save_sitemap(self, output_path=None):
        """Generate and save the sitemap"""
        if output_path is None:
            output_path = self.project_root / "public" / "sitemap.xml"
        
        sitemap_content = self.generate_sitemap()
        
        # Remove the XML declaration added by minidom
        lines = sitemap_content.split("\n")
        if lines[0].startswith("<?xml"):
            lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
        
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        
        print(f"✓ Sitemap generated: {output_path}")
        
        # Validate the sitemap
        url_count = sitemap_content.count("<url>")
        print(f"  Total URLs: {url_count}")


def main():
    """Main entry point"""
    generator = SitemapGenerator()
    generator.save_sitemap()


if __name__ == "__main__":
    main()