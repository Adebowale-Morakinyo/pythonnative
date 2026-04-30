package com.pythonnative.android_template;

import android.content.Context;
import android.util.TypedValue;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

/**
 * RecyclerView-backed fixed-height list used by PythonNative's Android bridge.
 *
 * <p>Chaquopy can proxy Java interfaces from Python, but it can't subclass Java
 * abstract classes such as RecyclerView.Adapter or RecyclerView.ViewHolder. This
 * helper owns those abstract-class implementations in Java and delegates row
 * content back to Python through the small Delegate interface below.</p>
 */
public class PNVirtualListView extends RecyclerView {
    public interface Delegate {
        int getCount();

        float getRowHeightDp();

        void mountRow(int position, FrameLayout container, float widthDp, float heightDp);

        void onRowPress(int position);
    }

    private final float density;
    private final RowAdapter rowAdapter;
    private Delegate delegate;

    public PNVirtualListView(@NonNull Context context, @NonNull Delegate delegate) {
        super(context);
        this.delegate = delegate;
        this.density = context.getResources().getDisplayMetrics().density;
        setLayoutManager(new LinearLayoutManager(context));
        setHasFixedSize(true);
        rowAdapter = new RowAdapter();
        setAdapter(rowAdapter);
    }

    public void setDelegate(@NonNull Delegate delegate) {
        this.delegate = delegate;
        rowAdapter.notifyDataSetChanged();
    }

    public void notifyDataChanged() {
        rowAdapter.notifyDataSetChanged();
    }

    private int rowHeightPx() {
        return Math.max(
            1,
            Math.round(TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP,
                delegate.getRowHeightDp(),
                getResources().getDisplayMetrics()
            ))
        );
    }

    private float currentWidthDp(FrameLayout container) {
        int widthPx = container.getWidth();
        if (widthPx <= 0) {
            widthPx = getWidth();
        }
        if (widthPx <= 0) {
            widthPx = getResources().getDisplayMetrics().widthPixels;
        }
        return widthPx / density;
    }

    private class RowHolder extends RecyclerView.ViewHolder {
        final FrameLayout container;

        RowHolder(@NonNull FrameLayout container) {
            super(container);
            this.container = container;
        }
    }

    private class RowAdapter extends RecyclerView.Adapter<RowHolder> {
        @Override
        public int getItemCount() {
            return delegate.getCount();
        }

        @NonNull
        @Override
        public RowHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            FrameLayout container = new FrameLayout(parent.getContext());
            container.setLayoutParams(
                new RecyclerView.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    rowHeightPx()
                )
            );
            return new RowHolder(container);
        }

        @Override
        public void onBindViewHolder(@NonNull RowHolder holder, int position) {
            RecyclerView.LayoutParams params = (RecyclerView.LayoutParams) holder.container.getLayoutParams();
            int heightPx = rowHeightPx();
            if (params.height != heightPx) {
                params.height = heightPx;
                holder.container.setLayoutParams(params);
            }
            holder.container.removeAllViews();
            holder.container.setOnClickListener(v -> delegate.onRowPress(holder.getBindingAdapterPosition()));
            delegate.mountRow(
                position,
                holder.container,
                currentWidthDp(holder.container),
                delegate.getRowHeightDp()
            );
        }

        @Override
        public void onViewRecycled(@NonNull RowHolder holder) {
            holder.container.removeAllViews();
            holder.container.setOnClickListener(null);
            super.onViewRecycled(holder);
        }
    }
}
