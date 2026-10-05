package dev.fancyvanilla.journal;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/**
 * The one quest the player is tracking. Kept in config/fancy_journal.json so it survives restarts;
 * a missing or broken file simply means "nothing tracked".
 */
public final class Tracker {
    private static final long DONE_SHOWN_MS = 4000;
    private static String tracked;
    private static long doneAt = -1;
    private static boolean loaded;
    private static String corner = "bottom_right";
    private static final java.util.Set<String> CORNERS = java.util.Set.of("top_left", "top_right", "bottom_left", "bottom_right");

    private Tracker() { }

    private static Path file() {
        return FabricLoader.getInstance().getConfigDir().resolve("fancy_journal.json");
    }

    private static void ensureLoaded() {
        if (loaded) return;
        loaded = true;
        try {
            Path file = file();
            if (Files.isRegularFile(file)) {
                JsonObject json = JsonParser.parseString(Files.readString(file, StandardCharsets.UTF_8)).getAsJsonObject();
                if (json.has("tracked") && !json.get("tracked").isJsonNull()) {
                    tracked = json.get("tracked").getAsString();
                }
                if (json.has("corner") && CORNERS.contains(json.get("corner").getAsString())) {
                    corner = json.get("corner").getAsString();
                }
            }
        } catch (IOException | RuntimeException e) {
            Journal.LOGGER.warn("Could not read the tracked quest, starting with none", e);
            tracked = null;
        }
    }

    private static void save() {
        try {
            JsonObject json = new JsonObject();
            json.addProperty("tracked", tracked);
            json.addProperty("corner", corner);  // top_left, top_right, bottom_left or bottom_right: edit the file to move the panel
            Files.writeString(file(), json + System.lineSeparator(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            Journal.LOGGER.warn("Could not save the tracked quest", e);
        }
    }

    public static synchronized String tracked() {
        ensureLoaded();
        return tracked;
    }

    public static synchronized String corner() {
        ensureLoaded();
        return corner;
    }

    public static synchronized boolean isTracked(String id) {
        return id != null && id.equals(tracked());
    }

    /** Track this quest, or stop tracking it when it is the tracked one. */
    public static synchronized void toggle(String id) {
        ensureLoaded();
        tracked = id.equals(tracked) ? null : id;
        doneAt = -1;
        save();
    }

    public static synchronized void clear() {
        ensureLoaded();
        tracked = null;
        doneAt = -1;
        save();
    }

    /** When the tracked quest is finished the panel stays a few seconds, then the quest is released. Returns true to keep drawing. */
    static synchronized boolean stillShowing(boolean done, long now) {
        if (!done) {
            doneAt = -1;
            return true;
        }
        if (doneAt < 0) {
            doneAt = now;
        }
        if (now - doneAt > DONE_SHOWN_MS) {
            clear();
            return false;
        }
        return true;
    }
}
