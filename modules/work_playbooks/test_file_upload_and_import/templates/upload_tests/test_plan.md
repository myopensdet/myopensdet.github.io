<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->

# Upload and import test plan: <feature name>

## 1. The rules (from the spec, or ask)

| Rule | Value |
| --- | --- |
| Upload address and form field | <POST /api/files, field "file"> |
| Allowed types | <PNG, JPEG, PDF> |
| Checked by name, or by content too? | <ask> |
| Size limit | <5 MB>. Is exactly 5 MB allowed? <ask> |
| Import columns | <email,name>; required: <both> |
| One bad row | <whole file refused / good rows saved / bad rows skipped> |
| Encoding | <UTF-8; Excel's "CSV UTF-8" adds a BOM> |
| Where the result can be read back | <GET /api/customers> |

## 2. Checks

| Kind | Check | Automated? |
| --- | --- | --- |
| Upload: good | Each allowed type is accepted; size is right | [ ] |
| Upload: limits | Exactly at the limit accepted; one byte over refused; empty refused | [ ] |
| Upload: type | Other types refused; a renamed file refused; double names like `photo.png.exe` refused | [ ] |
| Upload: name | Folder parts like `../../` dropped from the saved name | [ ] |
| Import: good | Every row saved; Excel file with BOM and accents works | [ ] |
| Import: bad | Bad row refuses the file (as the rule says) and names the row; wrong columns and wrong encoding give a clear message | [ ] |

## 3. Questions for the team

1. <e.g. Is the type checked by content, or only by the name?>

## 4. Not in this plan

- <Virus scanning: ask who owns it>
- <Very large imports (100,000 rows): a speed check>
