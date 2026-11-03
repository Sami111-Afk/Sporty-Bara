package ro.sportybara.app;

import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.fragment.app.Fragment;

import com.google.android.material.bottomnavigation.BottomNavigationView;

import ro.sportybara.app.ui.PlaceholderFragment;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        // Bara de jos își pune singură padding pentru bara de navigare a sistemului;
        // aici tratăm doar marginea de sus și lateralele.
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets bars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(bars.left, bars.top, bars.right, 0);
            return insets;
        });

        BottomNavigationView nav = findViewById(R.id.bottom_nav);
        nav.setOnItemSelectedListener(item -> {
            show(fragmentFor(item.getItemId()));
            return true;
        });
        if (savedInstanceState == null) {
            nav.setSelectedItemId(R.id.tab_home);
        }
    }

    private void show(Fragment f) {
        getSupportFragmentManager().beginTransaction()
                .replace(R.id.fragment_container, f)
                .commit();
    }

    /** Fiecare tab are deocamdată un ecran gol; se înlocuiesc pe rând cu ecranele reale. */
    private static Fragment fragmentFor(int tabId) {
        if (tabId == R.id.tab_tickets) {
            return PlaceholderFragment.newInstance(R.string.tab_tickets, R.string.empty_tickets);
        } else if (tabId == R.id.tab_wheel) {
            return PlaceholderFragment.newInstance(R.string.tab_wheel, R.string.empty_wheel);
        } else if (tabId == R.id.tab_leaderboard) {
            return PlaceholderFragment.newInstance(R.string.tab_leaderboard, R.string.empty_leaderboard);
        } else if (tabId == R.id.tab_profile) {
            return PlaceholderFragment.newInstance(R.string.tab_profile, R.string.empty_profile);
        }
        return PlaceholderFragment.newInstance(R.string.tab_home, R.string.empty_home);
    }
}
