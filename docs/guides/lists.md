# Lists

[`FlatList`][pythonnative.FlatList] and
[`SectionList`][pythonnative.SectionList] are the two list components
shipped with PythonNative. Both support **native virtualization**:
when you supply `item_height`, the list is backed by `UITableView` on
iOS and `RecyclerView` on Android, mounting rows lazily as they
scroll into view.

## When to virtualize

Virtualize whenever the list might exceed the viewport. The
non-virtualized fallback (`ScrollView` of every row) is only suitable
for short, fixed lists (a settings page, a small menu).

```python
import pythonnative as pn

items = [{"id": i, "title": f"Row {i}"} for i in range(10_000)]


@pn.component
def Big():
    return pn.FlatList(
        data=items,
        item_height=44,
        render_item=lambda item, _: pn.Text(item["title"]),
        key_extractor=lambda item, _: str(item["id"]),
    )
```

The list never holds 10,000 native views — only the rows currently
visible (plus a small reuse pool) ever exist.

## Pull-to-refresh

Use [`RefreshControl`][pythonnative.RefreshControl] as a prop on
either `FlatList` or [`ScrollView`][pythonnative.ScrollView]:

```python
@pn.component
def Pullable():
    refreshing, set_refreshing = pn.use_state(False)

    def reload():
        set_refreshing(True)
        # ... fetch data ...
        set_refreshing(False)

    return pn.FlatList(
        data=items,
        item_height=44,
        refresh_control=pn.RefreshControl(
            refreshing=refreshing,
            on_refresh=reload,
        ),
    )
```

## Row taps

Pass `on_item_press=` to receive the tapped row's index:

```python
pn.FlatList(
    data=items,
    item_height=44,
    on_item_press=lambda index: print(f"tapped {items[index]['id']}"),
)
```

Inside `render_item` you can also wrap the row in a
[`Pressable`][pythonnative.Pressable] for finer-grained control.

## Section lists

[`SectionList`][pythonnative.SectionList] flattens an iterable of
`{"title": ..., "data": [...]}` sections into a single virtualized
list, dispatching to either `render_section_header` or `render_item`
depending on the row's kind.

```python
sections = [
    {"title": "A", "data": ["Apple", "Avocado"]},
    {"title": "B", "data": ["Banana", "Blueberry"]},
]

pn.SectionList(
    sections=sections,
    item_height=44,
    section_header_height=32,
    render_section_header=lambda s, _: pn.Text(s["title"]),
    render_item=lambda item, _i, _s: pn.Text(item),
)
```

`item_height` and `section_header_height` are fixed; for variable-
height rows the eager fallback (omit `item_height`) is currently the
only option.

## Performance notes

- Always provide a stable `key_extractor` so reused rows refresh in
  place rather than tearing down and rebuilding their subtree.
- Keep row subtrees shallow. The reconciler is fast, but mounting a
  hundred `Text`/`Image`/`Button` nodes per row is wasteful work
  whenever a row recycles.
- Move expensive computation out of `render_item` (use
  [`use_memo`][pythonnative.use_memo] in the parent component, or
  pre-compute once before constructing the data list).
