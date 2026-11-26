# Reference

`aqua-hig-2002.pdf` is Apple's *Aqua Human Interface Guidelines*, June 2002 (308 pages),
the source for every measurement and sampled colour in this project (chapter 7 Controls,
chapter 8 Layout, chapter 10 Fonts).

It is © Apple Computer, Inc., so it is **not committed** (see `.gitignore`): publishing the
repo would otherwise redistribute Apple's document. To get the same file:

* A copy is hosted at <https://daringfireball.net/misc/2026/07/2002%20Aqua%20Human%20Interface%20Guidelines.pdf>
* SHA-256: `fb481487a58697f87f8f1ab4e17f8431c667864361c42acd2297af1828bb9a81`

Save it here as `reference/aqua-hig-2002.pdf`. To extract the control artwork losslessly for
pixel sampling:

```bash
mkdir -p /tmp/hig && pdfimages -png -p -f 120 -l 152 reference/aqua-hig-2002.pdf /tmp/hig/c
```
