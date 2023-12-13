# OHBM-ComCom-squarespace

## Transferring a post

1. Open the original blog page and the matching folder in [squarespace](squarespace).
2. Copy title.
3. Add images as necessary.
   * There are 2 ways of adding text beside an image:
      * Set the image to "Card" design and add text as the image subtitle.
        This keeps the image's original size.
      * Create a code/text block, then drag the block to the image's side.
        This lets you resize the image by dragging the border between blocks.
   * Some images may be missing. You will have to find and save those images from the original blog.
4. Insert code blocks around images and copy HTML from `text.html`.
   * Tables will need to be created in HTML or Markdown.
5. Compare with the original and make changes if necessary.
   You may need to create additional text/code/other blocks and edit manually.
   * Check [formatting notes](#formatting-notes)!
6. Open settings (click on date above title). Set the post Status (under Options) to "Needs Review".

## Reviewing a post

1. Open the post with EDIT. **Do NOT review using Squarespace's preview because it breaks some code!**
2. Text: Check spaces/line breaks, general formatting feel.
3. Image: Check that all images are present.
4. Add "By " at the start of the author line when appropriate. If you can (admins only), create a
   [basic author](https://support.squarespace.com/hc/en-us/articles/205810518) and change the author in settings.
   * If you can't set a single author in the settings (e.g. written by many people), you can hide the "Written By"
     line at the top using "Edit Section" (button on top right).
5. If everything looks good, open settings (click on date above title).
   * Content > Post URL: Match the original URL (`blog/article-name`).
   * Options > Status: Set "Published". Change the date to original's date in the past. Time can be whatever.

## Formatting notes

* Title: Default heading and font, no changes
* Author: Paragraph 1
* Subtitle: Paragraph 2 (color 3, dark blue)
* Section header: Heading 4
* Main text: Paragraph 2 (default)
   * Use natural margin between paragraphs rather than double line break.
* Image captions: Paragraph 3
* No indentation on paragraphs, just new line (this doesn't necessarily need to be consistent across sections)

## TODO

- [x] Organize by date
- [ ] Aggregate [basic authors](https://support.squarespace.com/hc/en-us/articles/205810518)
- [ ] Tags, categories?
