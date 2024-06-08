from rubicon.objc import ObjCClass


def main():
    """
    https://rubicon-objc.readthedocs.io/en/stable/tutorial/tutorial-1.html.
    """
    NSURL = ObjCClass("NSURL")
    base = NSURL.URLWithString("https://beeware.org/")
    full = NSURL.URLWithString("contributing/", relativeToURL=base)
    absolute = full.absoluteURL
    print(absolute.description)


if __name__ == "__main__":
    main()
