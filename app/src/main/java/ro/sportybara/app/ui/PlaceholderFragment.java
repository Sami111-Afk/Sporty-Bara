package ro.sportybara.app.ui;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.StringRes;
import androidx.fragment.app.Fragment;

import ro.sportybara.app.R;

/** Ecran gol pentru un tab, până se face ecranul real. */
public class PlaceholderFragment extends Fragment {

    private static final String ARG_TITLE = "title";
    private static final String ARG_MESSAGE = "message";

    public static PlaceholderFragment newInstance(@StringRes int title, @StringRes int message) {
        PlaceholderFragment f = new PlaceholderFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_TITLE, title);
        args.putInt(ARG_MESSAGE, message);
        f.setArguments(args);
        return f;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_placeholder, container, false);
        Bundle args = requireArguments();
        ((TextView) v.findViewById(R.id.title)).setText(args.getInt(ARG_TITLE));
        ((TextView) v.findViewById(R.id.message)).setText(args.getInt(ARG_MESSAGE));
        return v;
    }
}
