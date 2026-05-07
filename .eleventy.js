// Eleventy config for ctrl-alt-delete.ca
// Output: _site/ — published verbatim to GitHub Pages.

const { DateTime } = require("luxon");

module.exports = function (eleventyConfig) {
  // Pass through static assets (images, css, js, robots, CNAME)
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/robots.txt": "robots.txt" });
  eleventyConfig.addPassthroughCopy({ "CNAME": "CNAME" });
  eleventyConfig.addPassthroughCopy({ "src/favicon.ico": "favicon.ico" });

  // Watch CSS for live reload
  eleventyConfig.addWatchTarget("src/assets/css/");

  // ----- Filters -----
  eleventyConfig.addFilter("readableDate", (d) =>
    DateTime.fromJSDate(new Date(d), { zone: "utc" }).toFormat("LLLL d, yyyy")
  );
  eleventyConfig.addFilter("isoDate", (d) =>
    DateTime.fromJSDate(new Date(d), { zone: "utc" }).toISO()
  );
  eleventyConfig.addFilter("year", () => new Date().getFullYear());
  eleventyConfig.addFilter("titleCase", (s) =>
    String(s || "")
      .replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  );

  // ----- Collections -----
  eleventyConfig.addCollection("services", (api) =>
    api
      .getFilteredByGlob("src/services/*.md")
      .sort((a, b) => a.data.title.localeCompare(b.data.title))
  );
  eleventyConfig.addCollection("industries", (api) =>
    api
      .getFilteredByGlob("src/industries/*.md")
      .filter((p) => !p.inputPath.endsWith("index.md"))
      .sort((a, b) => a.data.title.localeCompare(b.data.title))
  );
  eleventyConfig.addCollection("locations", (api) =>
    api
      .getFilteredByGlob("src/locations-served/**/*.md")
      .filter((p) => p.data.category === "city")
      .sort((a, b) => a.data.title.localeCompare(b.data.title))
  );
  eleventyConfig.addCollection("projects", (api) =>
    api
      .getFilteredByGlob("src/projects/*.md")
      .filter((p) => !p.inputPath.endsWith("index.md"))
      .sort((a, b) => a.data.title.localeCompare(b.data.title))
  );
  eleventyConfig.addCollection("posts", (api) =>
    api
      .getFilteredByGlob("src/blog/posts/*.md")
      .sort((a, b) => new Date(b.data.date) - new Date(a.data.date))
  );

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site",
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    pathPrefix: "/",
  };
};
