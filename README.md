# OHBM-ComCom-squarespace

## Transferring a post

1. Open the original blog page and the matching folder in [squarespace](squarespace).
2. Copy title.
   * Beware of HTML that may carry over (check title in top bar) if copying from the original blog.
   * `metadata.json` includes sanitized title.
4. Add images.
   * You should rename the image to a more appropriate name whenever you can (e.g. the person's name).
   * Some images may be missing. You will have to find and save those images from the original blog.
   * For common images (like logos), avoid uploading duplicates. Try searching the image library ("Select from Library").
5. Add text. Insert code blocks around images and copy HTML from `text.html`.
   * Check [formatting notes](#formatting-notes)!
   * Tables will need to be created in HTML or Markdown.
6. Compare with the original and make changes if necessary.
   You may need to create additional text/code/other blocks and edit manually.
   * Feel free to improve upon the original if you can.
7. When you are done, open settings (click on date above title).
   * Content > Featured Image: Use "Search for Images" to choose a preview image among post images.
      * If the post has no image, you can default to a logo.
   * Options > Status: Set "Needs Review".

## Reviewing a post

1. Open the post with EDIT. **Do NOT review using Squarespace's preview because it breaks some code!**
2. Text: Check spaces/line breaks, general formatting feel.
3. Image: Check that all images are present.
4. Add "By " or "Author: " at the start of the author line when appropriate.
   * If you can (admins only), set the author in settings after creating a
     [basic author](https://support.squarespace.com/hc/en-us/articles/205810518).
     You may need to refresh the page for the new author to show up.
   * If you can't set a single author in the settings (e.g. written by many people),
     you can hide the "Written By" line at the top using "Edit Section" (button on top right).
5. If everything looks good, open settings (click on date above title).
   * Content > Post URL: Match the original URL (`blog/article-name`).
   * Options > Status: Set "Published". Change the date to original's date in the past. Time can be whatever.

## Formatting notes

### Text
* Title: Default heading and font, no all caps
* Author: Paragraph 1, no all caps
* Subtitle: Paragraph 2 (color 3, dark blue)
* Section header: Heading 4
* Main text: Paragraph 2 (default)
   * Use natural margin between paragraphs rather than double line break.
   * No indentation on paragraphs, just new line (this doesn't necessarily need to be consistent across sections)
* Image captions: Paragraph 3

### Image
There are 2 ways of adding text beside an image:
* Set the image to "Card" design and add text as the image subtitle.
  This keeps the image's original size.
* Create a code/text block, then drag the block to the image's side.
  This lets you resize the image by dragging the border between blocks.

## TODO

- [x] Organize by date
- [ ] Re-link all https://www.ohbmbrainmappingblog.com links
- [ ] Aggregate [basic authors](https://support.squarespace.com/hc/en-us/articles/205810518)
- [ ] Tags, categories?
