package dev.fancyvanilla.journal;

import dev.fancyvanilla.journal.mixin.ClientAdvancementsAccessor;
import java.util.List;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.advancements.AdvancementNode;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.multiplayer.ClientAdvancements;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundClientCommandPacket;
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Util;

/**
 * Panel in a screen corner while a quest is tracked: its name, what to do, a checklist of the requirements with live
 * counters (items are counted from the inventory), and a short "completed" message at the end.
 */
public final class TrackerHud implements HudElement {
    private static final int PANEL = 0xB4101319, BORDER = 0xFF2A303B, TEXT = 0xFFE8ECF2, MUTED = 0xFF9AA3B2;
    private static final int ACCENT = 0xFF8FB4E8, DONE = 0xFF7BD88F, TRACK = 0xFF2B313C, BOX = 0xFF5D6676;
    private static final int EDGE = 6, MAX_W = 232, MIN_W = 124, MAX_LINES = 6, ROW = 11;
    private static final long STATS_EVERY_MS = 5000;
    private static long lastStatsRequest;

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        String id = Tracker.tracked();
        if (id == null || mc.player == null || mc.getConnection() == null || mc.getDebugOverlay().showDebugScreen()) {
            return;
        }
        ClientAdvancements advancements = mc.getConnection().getAdvancements();
        ClientAdvancementsAccessor access = (ClientAdvancementsAccessor) advancements;
        AdvancementNode node = access.fancyJournal$tree().get(Identifier.parse(id));
        if (node == null || node.advancement().display().isEmpty()) {
            return; // not synced yet, or the quest no longer exists: keep the choice, draw nothing
        }
        DisplayInfo display = node.advancement().display().get();
        AdvancementProgress progress = access.fancyJournal$progress().get(node.holder());
        boolean done = progress != null && progress.isDone();
        if (!Tracker.stillShowing(done, Util.getMillis())) {
            return;
        }

        Font font = mc.font;
        QuestSpec spec = QuestSpec.of(id);
        if (spec != null && spec.usesStats() && !done && Util.getMillis() - lastStatsRequest > STATS_EVERY_MS) {
            lastStatsRequest = Util.getMillis();  // the server only sends statistics when asked, same request the statistics screen makes
            mc.getConnection().send(new ServerboundClientCommandPacket(ServerboundClientCommandPacket.Action.REQUEST_STATS));
        }
        List<QuestSpec.Line> lines = spec == null ? List.of() : spec.lines(progress, mc);
        int shown = Math.min(lines.size(), lines.size() > MAX_LINES ? MAX_LINES - 1 : MAX_LINES);
        int hidden = lines.size() - shown;

        Component header = Component.translatable(done ? "fancy_journal.hud.done" : "fancy_journal.hud.title");
        Component description = descriptionOf(display);
        FormattedCharSequence title = first(font, Compat.title(display), MAX_W - 20);
        List<FormattedCharSequence> descLines = font.split(description, MAX_W - 20);
        int descCount = Math.min(2, descLines.size());

        // fallback bar (quests we cannot read the conditions of): vanilla progress
        boolean vanillaBar = spec == null && !done && progress != null && progress.hasProgress();
        Component vanillaText = vanillaBar ? progress.getProgressText() : null;
        // overall bar for checklists with several steps or with a counter
        float fraction = -1f;
        if (!done && !lines.isEmpty()) {
            float sum = 0f;
            for (QuestSpec.Line line : lines) {
                sum += line.done() ? 1f : line.need() > 0 ? (float) line.have() / line.need() : 0f;
            }
            boolean countable = lines.size() > 1 || lines.get(0).need() > 1;
            fraction = countable ? sum / lines.size() : -1f;
        }
        boolean bar = vanillaBar || fraction >= 0f;

        int content = Math.max(font.width(header), font.width(title));
        for (int i = 0; i < descCount; i++) content = Math.max(content, font.width(descLines.get(i)));
        for (int i = 0; i < shown; i++) {
            QuestSpec.Line line = lines.get(i);
            content = Math.max(content, 12 + font.width(line.text()) + (line.need() > 1 ? 8 + font.width(counter(line)) : 0));
        }
        int width = Math.max(MIN_W, Math.min(MAX_W, content + 22));

        int height = 6 + 9 + 3 + 10 + (descCount > 0 ? 3 + descCount * 10 : 0) + (shown > 0 ? 4 + shown * ROW : 0)
                + (hidden > 0 ? ROW : 0) + (bar ? 9 : 0) + 6;
        String corner = Tracker.corner();
        final int x = corner.endsWith("right") ? g.guiWidth() - width - EDGE : EDGE;
        final int y = corner.startsWith("bottom") ? g.guiHeight() - height - EDGE : EDGE;

        g.fill(x, y, x + width, y + height, PANEL);
        g.fill(x, y, x + width, y + 1, BORDER);
        g.fill(x, y + height - 1, x + width, y + height, BORDER);
        g.fill(x + width - 1, y, x + width, y + height, BORDER);
        g.fill(x, y, x + 2, y + height, done ? DONE : ACCENT);
        int cy = y + 6;
        g.text(font, header, x + 8, cy, done ? DONE : MUTED, false);
        cy += 12;
        g.text(font, title, x + 8, cy, TEXT);
        cy += 10;
        if (descCount > 0) {
            cy += 3;
            for (int i = 0; i < descCount; i++) {
                g.text(font, descLines.get(i), x + 8, cy, MUTED, false);
                cy += 10;
            }
        }
        if (shown > 0) {
            cy += 4;
            for (int i = 0; i < shown; i++) {
                QuestSpec.Line line = lines.get(i);
                int color = line.done() ? DONE : TEXT;
                g.fill(x + 8, cy + 1, x + 15, cy + 8, line.done() ? DONE : BOX);
                if (!line.done()) g.fill(x + 9, cy + 2, x + 14, cy + 7, PANEL);
                String counter = line.need() > 1 ? counter(line) : "";
                int textW = width - 8 - 12 - 8 - (counter.isEmpty() ? 0 : font.width(counter) + 6);
                g.text(font, first(font, line.text(), Math.max(20, textW)), x + 19, cy, color, false);
                if (!counter.isEmpty()) {
                    g.text(font, counter, x + width - 8 - font.width(counter), cy, line.done() ? DONE : ACCENT, false);
                }
                cy += ROW;
            }
            if (hidden > 0) {
                g.text(font, Component.translatable("fancy_journal.hud.more", hidden), x + 19, cy, MUTED, false);
                cy += ROW;
            }
        }
        if (bar) {
            int barW = width - 16 - (vanillaText != null ? font.width(vanillaText) + 6 : 0);
            int by = cy + 3;
            float value = vanillaBar ? progress.getPercent() : fraction;
            g.fill(x + 8, by, x + 8 + Math.max(10, barW), by + 3, TRACK);
            g.fill(x + 8, by, x + 8 + Math.round(Math.max(10, barW) * Math.max(0f, Math.min(1f, value))), by + 3, ACCENT);
            if (vanillaText != null) {
                g.text(font, vanillaText, x + width - 8 - font.width(vanillaText), by - 3, ACCENT, false);
            }
        }
    }

    private static String counter(QuestSpec.Line line) {
        return line.have() + "/" + line.need();
    }

    private static FormattedCharSequence first(Font font, Component text, int width) {
        List<FormattedCharSequence> split = font.split(text, Math.max(10, width));
        return split.isEmpty() ? FormattedCharSequence.EMPTY : split.get(0);
    }

    /** TEMPERED optional quests carry a "(Optional, personal)" prefix that is just noise in the HUD. */
    private static Component descriptionOf(DisplayInfo display) {
        Component description = Compat.description(display);
        String text = description.getString();
        for (String prefix : List.of("(Opcjonalne, osobiste) ", "(Optional, personal) ")) {
            if (text.startsWith(prefix)) return Component.literal(text.substring(prefix.length()));
        }
        return description;
    }
}
