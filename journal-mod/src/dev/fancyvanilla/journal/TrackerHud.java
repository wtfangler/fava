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
import net.minecraft.resources.Identifier;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Util;

/** Small panel in the top-left corner while a quest is tracked: name, progress, and a short "done" message at the end. */
public final class TrackerHud implements HudElement {
    private static final int PANEL = 0xB4101319, BORDER = 0xFF2A303B, TEXT = 0xFFE8ECF2, MUTED = 0xFF9AA3B2;
    private static final int ACCENT = 0xFF8FB4E8, DONE = 0xFF7BD88F, TRACK = 0xFF2B313C;
    private static final int EDGE = 6, MAX_W = 190, MIN_W = 118;

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
        Component header = Component.translatable(done ? "fancy_journal.hud.done" : "fancy_journal.hud.title");
        List<FormattedCharSequence> titleLines = font.split(Compat.title(display), MAX_W - 20);
        FormattedCharSequence title = titleLines.isEmpty() ? FormattedCharSequence.EMPTY : titleLines.get(0);
        boolean bar = !done && progress != null && progress.hasProgress();
        Component progressText = bar ? progress.getProgressText() : null;

        int width = Math.max(MIN_W, Math.min(MAX_W, Math.max(font.width(header), font.width(title)) + 22));
        int height = 6 + 9 + 3 + 10 + (bar ? 8 : 0) + 6;
        String corner = Tracker.corner();
        final int X = corner.endsWith("right") ? g.guiWidth() - width - EDGE : EDGE;
        final int Y = corner.startsWith("bottom") ? g.guiHeight() - height - EDGE : EDGE;
        g.fill(X, Y, X + width, Y + height, PANEL);
        g.fill(X, Y, X + width, Y + 1, BORDER);
        g.fill(X, Y + height - 1, X + width, Y + height, BORDER);
        g.fill(X + width - 1, Y, X + width, Y + height, BORDER);
        g.fill(X, Y, X + 2, Y + height, done ? DONE : ACCENT);
        g.text(font, header, X + 8, Y + 6, done ? DONE : MUTED, false);
        g.text(font, title, X + 8, Y + 18, TEXT);
        if (bar) {
            int barW = width - 16 - (progressText != null ? font.width(progressText) + 6 : 0);
            int by = Y + 31;
            g.fill(X + 8, by, X + 8 + Math.max(10, barW), by + 3, TRACK);
            g.fill(X + 8, by, X + 8 + Math.max(0, Math.round(Math.max(10, barW) * progress.getPercent())), by + 3, ACCENT);
            if (progressText != null) {
                g.text(font, progressText, X + width - 8 - font.width(progressText), by - 3, ACCENT, false);
            }
        }
    }
}
