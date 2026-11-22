<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# File sharing: test ideas

## Works as it should

- Upload, download, and the downloaded file is exactly the same (compare a checksum)
- Share with one person: they can open it, others can't
- Change sharing from "can edit" to "can view", and remove access: it works at once
- A share link opens the file, and stops working when it's turned off or expires
- Rename, move and delete, and restore from the bin if the app has one

## Refuses bad input

- File types that aren't allowed, also when renamed (virus.exe called photo.jpg)
- Files over the size limit, and an empty (0 byte) file
- Sharing with an email that isn't valid

## Edges and limits

- Exactly the size limit, and the storage limit of the account
- File names with spaces, accents, emoji, very long names, and two files with the same name
- Upload the same file twice, and a new version of a shared file
- Slow connection: the upload can be stopped, and resumes or fails cleanly
- Delete a file someone else has open

## Security

- Change the file id in a download address: other people's files are refused
- An old share link can't be guessed (long random ids)
- Uploaded files are checked for viruses, if the app promises it
- Files that look like web pages (HTML, SVG) don't run scripts when opened

## People, devices and failures

- Two people edit or upload the same file at once
- Upload from a phone camera, and download on a phone
- Storage is down: a clear message, and no half-saved file is shown
