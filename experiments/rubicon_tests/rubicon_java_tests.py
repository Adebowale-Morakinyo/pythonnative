from rubicon.java import JavaClass


def main():
    """
    https://github.com/beeware/rubicon-java.
    """
    URL = JavaClass("java/net/URL")
    url = URL("https://beeware.org")
    print(url.getHost())


if __name__ == "__main__":
    main()
