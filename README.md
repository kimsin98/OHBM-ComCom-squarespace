# OHBM ComCom blog content transfer to Squarespace

## Prerequisite

You will need a Squarespace account and ask an admin for the "Website Editor" permission to add or edit posts. Join `#website` channel on Slack and notify Sin or Alfie to get started!

## Transferring a post

1. Open the original blog page and the matching folder in this repository's [squarespace](squarespace) directory. The spreadsheet row includes those links.
2. Create a new blog page by clicking "+" button under Pages > Blog > Blog Content.
3. Copy title from the `metadata.json` file.
   * Copying from the original blog may carry over additional HTML that we do not want.
4. Add images. They can be downloaded in order from the GitHub folder.
   * Some images may be missing or wrong. You will have to find the right images from the original blog or the [Internet Archive](https://web.archive.org/).
   * For common images (like logos), avoid uploading duplicates. Try searching the image library ("Select from Library").
   * Captions can be copied from `text.html` and styled manually or just copied from the original blog.
5. Add text. Insert code blocks between images and copy HTML from `text.html`.
   * Check [style guide](#style-guide) for more details like how to put text beside images!
   * Tables will need to be recreated in HTML or Markdown. If you are not sure how, skip it and add a TODO in the spreadsheet's "Notes" column.
6. Compare with the original and make changes if necessary.
   * Feel free to improve upon the original if you can. Note what you did in the "Notes" column.
   * If you can't fix some discrepancy, note it in the "Notes" column.
7. When you are done, open settings (click on date above title).
   * Content > Featured Image: Use "Search for Images" to choose a preview image among post images.
      * If the post has no image, you can default to a common logo.
   * Options > Status: Set "Needs Review".

The whole process takes ~15 min on average. Video guide:

[transferring.webm](https://github.com/user-attachments/assets/fd375501-0508-4ebd-8b02-66bb7e68a1ff)

## Reviewing a post

1. Open the post with EDIT. **Do NOT review using Squarespace's side preview because it breaks some code!**
2. Text: Check spaces/line breaks and general style consistency.
3. Image: Check that all images are present.
4. Add "By " or "Author: " before the author name when appropriate for clarity. Set the author from a dropdown in settings.
   * New basic authors can be only [created by admins](https://support.squarespace.com/hc/en-us/articles/205810518).
     Notify an admin if you can't create one.
   * You may need to refresh the page for the new basic author to show up.
6. If everything looks good, open settings (click on date above title).
   * Content > Post URL: Copy the original URL name from the spreadsheet (`blog/article-name`).
   * Options > Status: Set "Published". Change the date to original's date in the past. Time can be whatever.

## Style guide

### Text
* Title: Default heading and font, no all caps
* Author: Paragraph 1, no all caps
* Subtitle: Paragraph 2 (color 3, dark blue)
* Section header: Heading 4
* Main text: Paragraph 2 (default)
   * **Use natural margin between paragraphs rather than double line break.**
   * No indentation on paragraphs, just new line (this doesn't necessarily need to be consistent across sections)
* Image captions: Paragraph 3 (automatically applied now)

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
