from java import jclass, static_proxy, Override

LinearLayoutManager = jclass("androidx.recyclerview.widget.LinearLayoutManager")
RecyclerView = jclass("androidx.recyclerview.widget.RecyclerView")
TextView = jclass("android.widget.TextView")


# RecyclerView ViewHolder
class MyViewHolder(static_proxy(RecyclerView.ViewHolder)):
    def __init__(self, item_view):
        super(MyViewHolder, self).__init__(item_view)
        self.my_text_view = TextView(item_view.getContext())


# RecyclerView Adapter
class MyAdapter(static_proxy(RecyclerView.Adapter)):
    def __init__(self, my_dataset):
        self.my_dataset = my_dataset

    @Override(RecyclerView.Adapter)
    def onCreateViewHolder(self, parent, viewType):
        text_view = TextView(parent.getContext())
        return MyViewHolder(text_view)

    @Override(RecyclerView.Adapter)
    def onBindViewHolder(self, holder, position):
        holder.my_text_view.setText(self.my_dataset[position])

    @Override(RecyclerView.Adapter)
    def getItemCount(self):
        return len(self.my_dataset)


# Create the RecyclerView
def create_recycler_view(context):
    my_recycler_view = RecyclerView(context)
    my_layout_manager = LinearLayoutManager(context)
    my_recycler_view.setLayoutManager(my_layout_manager)
    my_dataset = ["Data 1", "Data 2", "Data 3"]
    my_adapter = MyAdapter(my_dataset)
    my_recycler_view.setAdapter(my_adapter)
    return my_recycler_view
