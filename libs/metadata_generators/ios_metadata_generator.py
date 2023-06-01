import clang.cindex
import json

clang.cindex.Config.set_library_path(
    "/Applications/Xcode.app/Contents/Developer/Toolchains/"
    "XcodeDefault.xctoolchain/usr/lib/"
)
index = clang.cindex.Index.create()


def extract(cursor):
    data = {"Name": cursor.spelling}
    if cursor.kind == clang.cindex.CursorKind.OBJC_INTERFACE_DECL:
        data["Type"] = "Interface"
    elif cursor.kind in [
        clang.cindex.CursorKind.OBJC_INSTANCE_METHOD_DECL,
        clang.cindex.CursorKind.OBJC_CLASS_METHOD_DECL,
    ]:
        data["Type"] = "Method"
    elif cursor.kind == clang.cindex.CursorKind.OBJC_PROPERTY_DECL:
        data["Type"] = "Property"
    else:
        return None
    children = [extract(c) for c in cursor.get_children()]
    children = [c for c in children if c is not None]
    if children:
        data["Children"] = children
    return data


def main():
    tu = index.parse(
        "/Applications/Xcode.app/Contents/Developer/Platforms/"
        "iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/"
        "Library/Frameworks/UIKit.framework/Headers/UIKit.h"
    )
    metadata = extract(tu.cursor)
    with open("metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    main()
