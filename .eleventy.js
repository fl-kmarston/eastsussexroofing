module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/static": "/" });
  eleventyConfig.addWatchTarget("src/static/");
  eleventyConfig.addFilter("dateReadable", (value) => value);
  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "dist" },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};
