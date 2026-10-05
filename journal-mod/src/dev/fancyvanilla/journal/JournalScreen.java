package dev.fancyvanilla.journal;

import com.mojang.blaze3d.platform.cursor.CursorTypes;
import com.mojang.blaze3d.platform.InputConstants;
import dev.fancyvanilla.journal.mixin.ClientAdvancementsAccessor;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.advancements.AdvancementNode;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.multiplayer.ClientAdvancements;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundSeenAdvancementsPacket;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;

/**
 * Fancy Vanilla journal: a flat, restrained replacement for the advancements screen.
 * Left: tabs (one per root advancement, e.g. a Tempered era) with progress. Right: search, filters and a card grid.
 */
public class JournalScreen extends Screen {
    // palette (ARGB)
    private static final int PANEL = 0xF2111318, SIDEBAR = 0xFF15181E, CARD = 0xFF1B1F27, CARD_HOVER = 0xFF232935;
    private static final int BORDER = 0xFF2A303B, TEXT = 0xFFE8ECF2, MUTED = 0xFF9AA3B2, ACCENT = 0xFF8FB4E8;
    private static final int DONE = 0xFF7BD88F, GOLD = 0xFFF2C14E, PURPLE = 0xFFC78BFF, TRACK = 0xFF2B313C;

    private static final int MARGIN = 12, MAX_W = 980, HEADER_H = 34, SIDEBAR_W = 150, TAB_H = 32, TOOLBAR_H = 24;
    private static final int CARD_MIN_W = 190, CARD_H = 48, GAP = 6, PAD = 8;

    // remembered between openings
    private static int rememberedTab;
    private static String rememberedRoot;
    private static Filter rememberedFilter = Filter.ALL;

    private enum Filter {
        ALL("fancy_journal.filter.all"), ACTIVE("fancy_journal.filter.active"), DONE("fancy_journal.filter.done");
        final String key;
        Filter(String key) { this.key = key; }
    }

    private record Entry(AdvancementHolder holder, DisplayInfo display, AdvancementProgress progress, ItemStack icon) {
        boolean done() { return progress != null && progress.isDone(); }
        boolean optional() { return holder.id().toString().startsWith("tempered:bonus/"); }
    }

    private record Tab(AdvancementNode root, DisplayInfo display, ItemStack icon, List<Entry> entries, int done, int required, int requiredDone) {
        int optional() { return entries.size() - required(); }
        int optionalDone() { return done - requiredDone(); }
        /** Counter for the sidebar: required quests, or every quest for branches that only have optional ones (Epilog). */
        int shownTotal() { return required > 0 ? required : entries.size(); }
        int shownDone() { return required > 0 ? requiredDone : done; }
    }

    private final ClientAdvancements advancements;
    private final Screen lastScreen;
    private List<Tab> tabs = List.of();
    private List<Entry> filteredEntries;
    private final Map<AdvancementHolder, ItemStack> icons = new HashMap<>();
    private final List<Control> tabControls = new ArrayList<>();
    private final List<Control> filterControls = new ArrayList<>();
    private Control classicControl;
    private int selected;
    private String selectedId = rememberedRoot;
    private Filter filter = rememberedFilter;
    private String query = "";
    private double scroll;
    private double sidebarScroll;
    private long revision = Long.MIN_VALUE;
    private int ticks;
    private boolean laidOut;
    private EditBox search;

    // layout (recomputed in init)
    private int px, py, pw, ph, sbX, sbY, sbH, cx, cy, cw, vx, vy, vw, vh;
    private int chipX, chipY, chipW, classicX, classicW, sidebarW, searchW, toolbarH;

    public JournalScreen(ClientAdvancements advancements, Screen lastScreen) {
        super(Component.translatable("fancy_journal.title"));
        this.advancements = advancements;
        this.lastScreen = lastScreen;
        this.selected = rememberedTab;
    }

    public ClientAdvancements advancements() { return advancements; }

    public Screen lastScreen() { return lastScreen; }

    // ------------------------------------------------------------------ data

    private void rebuild() {
        ClientAdvancementsAccessor access = (ClientAdvancementsAccessor) advancements;
        Map<AdvancementHolder, AdvancementProgress> progress = access.fancyJournal$progress();
        List<Tab> result = new ArrayList<>();
        List<AdvancementNode> roots = new ArrayList<>();
        access.fancyJournal$tree().roots().forEach(roots::add);
        roots.sort(Comparator.comparingInt((AdvancementNode root) -> root.holder().id().toString().startsWith("tempered:age/") ? 0 : 1)
                .thenComparing(root -> root.holder().id().toString(), NaturalOrder::compare));
        for (AdvancementNode root : roots) {
            Optional<DisplayInfo> display = root.advancement().display();
            AdvancementProgress rootProgress = progress.get(root.holder());
            if (display.isEmpty() || Compat.hidden(display.get()) && (rootProgress == null || !rootProgress.isDone())) {
                continue;
            }
            List<Entry> entries = new ArrayList<>();
            // Tempered roots mark eras or the Epilog branch; vanilla roots are real tasks with their own criteria.
            if (!root.holder().id().toString().startsWith("tempered:")) {
                addEntry(root, progress, entries);
            }
            collect(root, progress, entries);
            entries.sort(Comparator.comparing(Entry::optional)
                    .thenComparing(e -> e.holder().id().toString(), NaturalOrder::compare));
            int done = (int) entries.stream().filter(Entry::done).count();
            int required = (int) entries.stream().filter(e -> !e.optional()).count();
            int requiredDone = (int) entries.stream().filter(e -> !e.optional() && e.done()).count();
            result.add(new Tab(root, display.get(), icon(root.holder(), display.get()), entries, done, required, requiredDone));
        }
        tabs = result;
        if (selectedId != null) {
            selected = -1;
            for (int i = 0; i < tabs.size(); i++) {
                if (tabs.get(i).root().holder().id().toString().equals(selectedId)) selected = i;
            }
        }
        if (selected < 0 || selected >= tabs.size()) {
            selected = 0;
        }
        String previousId = selectedId;
        selectedId = tabs.isEmpty() ? null : tabs.get(selected).root().holder().id().toString();
        if (!java.util.Objects.equals(previousId, selectedId)) scroll = 0;
        filteredEntries = null;
        icons.keySet().retainAll(progress.keySet());
        if (laidOut) refreshTabControls();
    }

    private ItemStack icon(AdvancementHolder holder, DisplayInfo display) {
        return icons.computeIfAbsent(holder, ignored -> Compat.icon(display));
    }

    private void addEntry(AdvancementNode node, Map<AdvancementHolder, AdvancementProgress> progress, List<Entry> out) {
        node.advancement().display().ifPresent(display -> {
            AdvancementProgress state = progress.get(node.holder());
            if (!Compat.hidden(display) || state != null && state.isDone()) {
                out.add(new Entry(node.holder(), display, state, icon(node.holder(), display)));
            }
        });
    }

    private void collect(AdvancementNode node, Map<AdvancementHolder, AdvancementProgress> progress, List<Entry> out) {
        for (AdvancementNode child : node.children()) {
            addEntry(child, progress, out);
            collect(child, progress, out);
        }
    }

    private List<Entry> visibleEntries() {
        if (filteredEntries != null) return filteredEntries;
        if (tabs.isEmpty()) {
            return List.of();
        }
        String q = query.toLowerCase(Locale.ROOT);
        List<Entry> out = new ArrayList<>();
        for (Entry e : tabs.get(selected).entries()) {
            if (filter == Filter.DONE && !e.done()) continue;
            if (filter == Filter.ACTIVE && e.done()) continue;
            if (!q.isEmpty() && !Compat.title(e.display()).getString().toLowerCase(Locale.ROOT).contains(q)
                    && !Compat.description(e.display()).getString().toLowerCase(Locale.ROOT).contains(q)) continue;
            out.add(e);
        }
        filteredEntries = out;
        return filteredEntries;
    }

    // ------------------------------------------------------------------ lifecycle / layout

    @Override
    protected void init() {
        try {
            initialize();
        } catch (RuntimeException e) {
            fallBack(e);
        }
    }

    private void initialize() {
        laidOut = false;
        tabControls.clear();
        filterControls.clear();
        rebuild();
        revision = dataRevision();
        Journal.LOGGER.info("Journal opened: {} tab(s), {}x{} gui", tabs.size(), width, height);
        pw = Math.min(MAX_W, width - 2 * MARGIN);
        ph = height - 2 * MARGIN;
        px = (width - pw) / 2;
        py = MARGIN;
        sbX = px;
        sbY = py + HEADER_H;
        sbH = ph - HEADER_H;
        sidebarW = Math.min(SIDEBAR_W, Math.max(100, pw / 4));
        cx = px + sidebarW;
        cy = py + HEADER_H;
        cw = pw - sidebarW;
        vx = cx + PAD;
        vw = cw - PAD * 2;
        int filtersW = 3 * 64 + 2 * GAP;
        boolean compact = vw < 160 + GAP + filtersW;
        searchW = compact ? vw : 160;
        toolbarH = compact ? TOOLBAR_H + 22 : TOOLBAR_H;
        vy = cy + toolbarH + PAD * 2;
        vh = py + ph - vy - PAD;
        chipW = compact ? (vw - 2 * GAP) / 3 : 64;
        chipX = compact ? vx : vx + searchW + GAP;
        chipY = cy + PAD + (compact ? 22 : 0);
        classicW = Math.min(110, font.width(Component.translatable("fancy_journal.classic")) + 14);
        classicX = px + pw - classicW - PAD;

        search = new EditBox(font, vx, cy + PAD, searchW, 16, Component.translatable("fancy_journal.search"));
        search.setHint(Component.translatable("fancy_journal.search"));
        search.setMaxLength(40);
        search.setValue(query);
        search.setResponder(text -> {
            query = text;
            scroll = 0;
            filteredEntries = null;
        });
        addRenderableWidget(search);
        for (int i = 0; i < Filter.values().length; i++) {
            Filter value = Filter.values()[i];
            Control control = new Control(chipX + i * (chipW + GAP), chipY, chipW, 16,
                    Component.translatable(value.key), () -> {
                        filter = value;
                        scroll = 0;
                        filteredEntries = null;
                    });
            filterControls.add(addRenderableWidget(control));
        }
        classicControl = addRenderableWidget(new Control(classicX, py + 8, classicW, 18,
                Component.translatable("fancy_journal.classic"), () -> Journal.openClassic(minecraft, this)));
        laidOut = true;
        refreshTabControls();
        ensureTabVisible();

        if (!tabs.isEmpty()) {
            advancements.setSelectedTab(tabs.get(selected).root().holder(), true);
        }
    }

    @Override
    public void tick() {
        super.tick();
        try {
            long next = dataRevision();
            if (next != revision) {
                rebuild();
                revision = next;
            }
        } catch (RuntimeException e) {
            fallBack(e);
        }
    }

    private long dataRevision() {
        // Optional mixin failures still leave a usable screen with a conservative one-second refresh.
        return advancements instanceof AdvancementUpdates updates ? updates.fancyJournal$revision() : ticks++ / 20;
    }

    /** Real widgets supply focus, keyboard activation, narration and tooltip behavior; paint stays custom. */
    private final class Control extends AbstractWidget {
        private final Runnable action;

        private Control(int x, int y, int w, int h, Component label, Runnable action) {
            super(x, y, w, h, label);
            this.action = action;
        }

        @Override protected void extractWidgetRenderState(GuiGraphicsExtractor g, int x, int y, float tick) { }
        @Override protected void updateWidgetNarration(NarrationElementOutput out) { defaultButtonNarrationText(out); }
        @Override public void onClick(MouseButtonEvent event, boolean doubleClick) {
            action.run();
        }
        @Override public boolean keyPressed(KeyEvent event) {
            if (active && visible && event.isConfirmation()) {
                playDownSound(minecraft.getSoundManager());
                action.run();
                return true;
            }
            return false;
        }
    }

    private List<String> controlRoots = List.of();

    private void refreshTabControls() {
        List<String> roots = tabs.stream().map(t -> t.root().holder().id().toString()).toList();
        if (tabControls.size() != tabs.size() || !controlRoots.equals(roots)) {
            for (Control control : tabControls) {
                if (control.isFocused()) clearFocus();
                removeWidget(control);
            }
            tabControls.clear();
            for (int i = 0; i < tabs.size(); i++) {
                int index = i;
                tabControls.add(addRenderableWidget(new Control(sbX + 4, sbY, sidebarW - 9, TAB_H,
                        Compat.title(tabs.get(i).display()), () -> selectTab(index))));
            }
            controlRoots = roots;
        }
        for (int i = 0; i < tabs.size(); i++) {
            Tab tab = tabs.get(i);
            tabControls.get(i).setMessage(Component.empty().append(Compat.title(tab.display())).append(" " + tab.shownDone() + "/" + tab.shownTotal()));
            Component hint = Component.empty().append(Compat.title(tab.display())).append("\n").append(Compat.description(tab.display()));
            if (tab.optional() > 0) {
                hint = Component.empty().append(hint).append("\n\n").append(Component.translatable("fancy_journal.optional_summary", tab.optionalDone(), tab.optional()));
            }
            tabControls.get(i).setTooltip(Tooltip.create(hint));
        }
        positionTabControls();
    }

    private void positionTabControls() {
        double max = Math.max(0, tabs.size() * (TAB_H + 2) - 2 + PAD * 2 - sbH);
        sidebarScroll = Math.max(0, Math.min(sidebarScroll, max));
        for (int i = 0; i < tabControls.size(); i++) {
            int y = sbY + PAD + i * (TAB_H + 2) - (int) sidebarScroll;
            int top = Math.max(sbY, y), bottom = Math.min(sbY + sbH - 1, y + TAB_H);
            Control control = tabControls.get(i);
            control.setY(top);
            control.setHeight(Math.max(0, bottom - top));
            control.visible = bottom > top;
        }
    }

    private void ensureTabVisible() {
        int y = PAD + selected * (TAB_H + 2);
        if (y < sidebarScroll) sidebarScroll = y;
        if (y + TAB_H > sidebarScroll + sbH) sidebarScroll = y + TAB_H - sbH;
        positionTabControls();
    }

    @Override
    protected void setInitialFocus() {
        // Opening with the advancement key should allow pressing the same key to close.
    }

    private boolean failed;

    /** Safety net: never crash the game because of the journal, return to the classic screen instead. */
    private void fallBack(RuntimeException e) {
        if (!failed) {
            failed = true;
            Journal.LOGGER.error("Journal failed, switching to the classic advancements screen", e);
            Journal.openClassic(minecraft, this);
        }
    }

    @Override
    public void onClose() {
        minecraft.setScreenAndShow(lastScreen);
    }

    @Override
    public void removed() {
        rememberedTab = selected;
        rememberedRoot = selectedId;
        rememberedFilter = filter;
        ClientPacketListener connection = minecraft.getConnection();
        if (connection != null) {
            connection.send(ServerboundSeenAdvancementsPacket.closedScreen());
        }
    }

    @Override
    public boolean isPauseScreen() {
        return true;
    }

    // ------------------------------------------------------------------ input

    @Override
    public boolean keyPressed(KeyEvent event) {
        if ((minecraft.options.keyAdvancements.matches(event)
                || FancyJournalClient.OPEN_JOURNAL != null && FancyJournalClient.OPEN_JOURNAL.matches(event)) && !search.isFocused()) {
            if (FancyJournalClient.OPEN_JOURNAL != null) {
                while (FancyJournalClient.OPEN_JOURNAL.consumeClick()) { }
            }
            onClose();
            return true;
        }
        if (!search.isFocused()) {
            if (event.hasControlDown() && (event.key() == InputConstants.KEY_PAGEUP || event.key() == InputConstants.KEY_PAGEDOWN) && !tabs.isEmpty()) {
                int direction = event.key() == InputConstants.KEY_PAGEUP ? -1 : 1;
                selectTab(Math.floorMod(selected + direction, tabs.size()));
                return true;
            }
            switch (event.key()) {
                case InputConstants.KEY_PAGEUP -> scroll -= Math.max(CARD_H, vh - CARD_H);
                case InputConstants.KEY_PAGEDOWN -> scroll += Math.max(CARD_H, vh - CARD_H);
                case InputConstants.KEY_HOME -> scroll = 0;
                case InputConstants.KEY_END -> scroll = contentHeight(visibleEntries().size());
                default -> { return super.keyPressed(event); }
            }
            clampScroll();
            return true;
        }
        return super.keyPressed(event);
    }

    @Override
    public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
        return super.mouseClicked(event, doubleClick);
    }

    private void selectTab(int index) {
        if (index == selected) {
            return;
        }
        selected = index;
        selectedId = tabs.get(index).root().holder().id().toString();
        scroll = 0;
        filteredEntries = null;
        ensureTabVisible();
        advancements.setSelectedTab(tabs.get(index).root().holder(), true);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double scrollX, double scrollY) {
        if (mx >= sbX && mx < sbX + sidebarW && my >= sbY && my < sbY + sbH) {
            sidebarScroll -= scrollY * (TAB_H + 2);
            positionTabControls();
            return true;
        }
        if (mx >= vx && mx < vx + vw && my >= vy && my < vy + vh) {
            scroll -= scrollY * 24;
            clampScroll();
            return true;
        }
        return super.mouseScrolled(mx, my, scrollX, scrollY);
    }

    private int columns() {
        return Math.max(1, (vw + GAP) / (CARD_MIN_W + GAP));
    }

    private int contentHeight(int count) {
        int rows = (count + columns() - 1) / columns();
        return rows == 0 ? 0 : rows * (CARD_H + GAP) - GAP;
    }

    private void clampScroll() {
        double max = Math.max(0, contentHeight(visibleEntries().size()) - vh);
        scroll = Math.max(0, Math.min(scroll, max));
    }

    // ------------------------------------------------------------------ rendering

    private static void rounded(GuiGraphicsExtractor g, int x, int y, int w, int h, int color) {
        g.fill(x + 1, y, x + w - 1, y + h, color);
        g.fill(x, y + 1, x + w, y + h - 1, color);
    }

    private static int frameColor(DisplayInfo d) {
        return switch (Compat.type(d)) {
            case CHALLENGE -> PURPLE;
            case GOAL -> GOLD;
            default -> ACCENT;
        };
    }

    private void bar(GuiGraphicsExtractor g, int x, int y, int w, float fraction, int color) {
        g.fill(x, y, x + w, y + 3, TRACK);
        int filled = Math.round(w * Math.max(0f, Math.min(1f, fraction)));
        if (filled > 0) {
            g.fill(x, y, x + filled, y + 3, color);
        }
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, int mouseX, int mouseY, float partialTick) {
        if (failed) {
            return;
        }
        try {
            draw(g, mouseX, mouseY, partialTick);
        } catch (RuntimeException e) {
            try {
                g.disableScissor();
            } catch (RuntimeException ignored) {
                // no scissor was active
            }
            fallBack(e);
        }
    }

    private void draw(GuiGraphicsExtractor g, int mouseX, int mouseY, float partialTick) {
        clampScroll();
        rounded(g, px, py, pw, ph, PANEL);
        g.outline(px, py, pw, ph, BORDER);

        drawHeader(g, mouseX, mouseY);
        drawSidebar(g, mouseX, mouseY);
        drawToolbar(g, mouseX, mouseY);
        List<Component> tooltip = drawCards(g, mouseX, mouseY);

        super.extractRenderState(g, mouseX, mouseY, partialTick); // search box on top
        if (tooltip != null) {
            g.setComponentTooltipForNextFrame(font, tooltip, mouseX, mouseY);
        }
    }

    private void drawHeader(GuiGraphicsExtractor g, int mouseX, int mouseY) {
        g.text(font, title, px + PAD + 4, py + 12, TEXT);
        int total = tabs.stream().mapToInt(t -> t.entries().size()).sum();
        int done = tabs.stream().mapToInt(Tab::done).sum();
        Component summary = Component.translatable("fancy_journal.summary", done, total);
        int summaryX = classicX - font.width(summary) - 12;
        if (summaryX >= px + PAD + 4 + font.width(title) + 12) {
            g.text(font, summary, summaryX, py + 12, MUTED);
        }
        // classic view button
        boolean hover = classicControl.isMouseOver(mouseX, mouseY) || classicControl.isFocused();
        rounded(g, classicX, py + 8, classicW, 18, hover ? CARD_HOVER : CARD);
        if (hover) {
            g.requestCursor(CursorTypes.POINTING_HAND);
        }
        g.centeredText(font, Component.translatable("fancy_journal.classic"), classicX + classicW / 2, py + 13, hover ? TEXT : MUTED);
        // overall progress under the header
        g.fill(px, py + HEADER_H - 2, px + pw, py + HEADER_H, TRACK);
        if (total > 0) {
            g.fill(px, py + HEADER_H - 2, px + Math.round(pw * (done / (float) total)), py + HEADER_H, ACCENT);
        }
    }

    private void drawSidebar(GuiGraphicsExtractor g, int mouseX, int mouseY) {
        g.fill(sbX, sbY, sbX + sidebarW, py + ph - 1, SIDEBAR);
        g.fill(sbX + sidebarW - 1, sbY, sbX + sidebarW, py + ph - 1, BORDER);
        g.enableScissor(sbX, sbY, sbX + sidebarW, py + ph - 1);
        for (int i = 0; i < tabs.size(); i++) {
            Tab tab = tabs.get(i);
            int ty = sbY + PAD + i * (TAB_H + 2) - (int) sidebarScroll;
            boolean sel = i == selected;
            Control control = tabControls.get(i);
            if (!control.visible) continue;
            boolean hover = control.isMouseOver(mouseX, mouseY) || control.isFocused();
            if (sel || hover) {
                rounded(g, sbX + 4, ty, sidebarW - 9, TAB_H, sel ? CARD_HOVER : CARD);
            }
            if (sel) {
                g.fill(sbX + 4, ty + 4, sbX + 6, ty + TAB_H - 4, ACCENT);
            }
            g.item(tab.icon(), sbX + 10, ty + 8);
            List<FormattedCharSequence> lines = font.split(Compat.title(tab.display()), sidebarW - 42);
            if (!lines.isEmpty()) {
                g.text(font, lines.get(0), sbX + 32, ty + 6, sel ? TEXT : MUTED);
            }
            int total = tab.shownTotal();
            int done = tab.shownDone();
            float fraction = total == 0 ? 0 : done / (float) total;
            String count = done + "/" + total;
            int countW = font.width(count);
            int barW = Math.max(0, sidebarW - 44 - countW - 6);
            bar(g, sbX + 32, ty + 21, barW, fraction, fraction >= 1f ? DONE : ACCENT);
            g.text(font, count, sbX + 32 + barW + 6, ty + 18, fraction >= 1f ? DONE : MUTED, false);
            if (hover) {
                g.requestCursor(CursorTypes.POINTING_HAND);
            }
        }
        g.disableScissor();
        int content = tabs.size() * (TAB_H + 2) - 2 + PAD * 2;
        if (content > sbH) {
            int thumbH = Math.max(12, sbH * sbH / content);
            int thumbY = sbY + (int) ((sbH - thumbH) * sidebarScroll / (content - sbH));
            g.fill(sbX + sidebarW - 3, thumbY, sbX + sidebarW - 1, thumbY + thumbH, 0xFF3A4252);
        }
    }

    private void drawToolbar(GuiGraphicsExtractor g, int mouseX, int mouseY) {
        for (int i = 0; i < Filter.values().length; i++) {
            Filter f = Filter.values()[i];
            int fx = chipX + i * (chipW + GAP);
            boolean sel = f == filter;
            Control control = filterControls.get(i);
            boolean hover = control.isMouseOver(mouseX, mouseY) || control.isFocused();
            rounded(g, fx, chipY, chipW, 16, sel ? ACCENT : hover ? CARD_HOVER : CARD);
            Component label = Component.translatable(f.key);
            String text = font.plainSubstrByWidth(label.getString(), Math.max(0, chipW - 4));
            g.text(font, text, fx + (chipW - font.width(text)) / 2, chipY + 4, sel ? 0xFF10141A : MUTED, !sel);
            if (hover) {
                g.requestCursor(CursorTypes.POINTING_HAND);
            }
        }
        g.fill(cx + PAD, cy + toolbarH + PAD + 2, cx + cw - PAD, cy + toolbarH + PAD + 3, BORDER);
    }

    /** Draws the grid and returns tooltip lines for the hovered card, or null. */
    private List<Component> drawCards(GuiGraphicsExtractor g, int mouseX, int mouseY) {
        if (tabs.isEmpty()) {
            g.centeredText(font, Component.translatable("fancy_journal.empty"), cx + cw / 2, cy + ph / 2 - 20, MUTED);
            return null;
        }
        List<Entry> entries = visibleEntries();
        if (entries.isEmpty()) {
            g.centeredText(font, Component.translatable("fancy_journal.none"), cx + cw / 2, vy + 24, MUTED);
            return null;
        }
        int cols = columns();
        int cardW = (vw - (cols - 1) * GAP) / cols;
        List<Component> tooltip = null;
        g.enableScissor(vx, vy, vx + vw, vy + vh);
        for (int i = 0; i < entries.size(); i++) {
            Entry e = entries.get(i);
            int x = vx + (i % cols) * (cardW + GAP);
            int y = vy + (i / cols) * (CARD_H + GAP) - (int) scroll;
            if (y + CARD_H < vy || y > vy + vh) {
                continue;
            }
            boolean hover = mouseX >= x && mouseX < x + cardW && mouseY >= Math.max(y, vy) && mouseY < Math.min(y + CARD_H, vy + vh);
            drawCard(g, e, x, y, cardW, hover);
            if (hover) {
                tooltip = tooltipFor(e);
            }
        }
        g.disableScissor();
        // thin scrollbar
        int content = contentHeight(entries.size());
        if (content > vh) {
            int trackH = vh;
            int thumbH = Math.max(18, trackH * vh / content);
            int thumbY = vy + (int) ((trackH - thumbH) * (scroll / (content - vh)));
            g.fill(vx + vw + 2, thumbY, vx + vw + 4, thumbY + thumbH, 0xFF3A4252);
        }
        return tooltip;
    }

    private void drawCard(GuiGraphicsExtractor g, Entry e, int x, int y, int w, boolean hover) {
        boolean done = e.done();
        rounded(g, x, y, w, CARD_H, hover ? CARD_HOVER : CARD);
        int stripe = done ? DONE : frameColor(e.display());
        g.fill(x, y + 2, x + 2, y + CARD_H - 2, done ? DONE : (stripe & 0x00FFFFFF) | 0x66000000);
        g.item(e.icon(), x + 10, y + 8);
        int textX = x + 36;
        int textW = Math.max(1, w - 36 - 22);
        int statusW = !done && e.progress() != null && e.progress().hasProgress() && e.progress().getProgressText() != null
                ? font.width(e.progress().getProgressText()) + 8 : 0;
        Component optional = Component.translatable("fancy_journal.optional");
        int optionalW = e.optional() ? font.width(optional) + 8 : 0;
        List<FormattedCharSequence> titleLines = font.split(Compat.title(e.display()), Math.max(1, textW - statusW - optionalW));
        if (!titleLines.isEmpty()) {
            g.text(font, titleLines.get(0), textX, y + 6, done ? TEXT : 0xFFD3D9E3);
        }
        if (e.optional()) {
            g.text(font, optional, x + w - 22 - statusW - font.width(optional), y + 7, GOLD, false);
        }
        Component description = Compat.description(e.display());
        if (e.optional()) {
            String text = description.getString();
            for (String prefix : List.of("(Opcjonalne, osobiste) ", "(Optional, personal) ")) {
                if (text.startsWith(prefix)) {
                    description = Component.literal(text.substring(prefix.length()));
                    break;
                }
            }
        }
        List<FormattedCharSequence> desc = font.split(description, textW);
        for (int l = 0; l < Math.min(2, desc.size()); l++) {
            g.text(font, desc.get(l), textX, y + 18 + l * 10, MUTED);
        }
        // status mark (top right): a small filled square when done
        if (done) {
            g.fill(x + w - 16, y + 7, x + w - 8, y + 15, DONE);
            g.fill(x + w - 14, y + 9, x + w - 10, y + 13, 0xFF10261A);
        } else if (e.progress() != null && e.progress().hasProgress() && e.progress().getProgressText() != null) {
            Component text = e.progress().getProgressText();
            g.text(font, text, x + w - 8 - font.width(text), y + 7, ACCENT);
        }
        if (!done && e.progress() != null && e.progress().hasProgress()) {
            bar(g, textX, y + CARD_H - 6, textW, e.progress().getPercent(), ACCENT);
        }
    }

    private List<Component> tooltipFor(Entry e) {
        List<Component> lines = new ArrayList<>();
        lines.add(Compat.title(e.display()));
        lines.add(Compat.description(e.display()));
        if (e.optional()) {
            lines.add(Component.translatable("fancy_journal.optional_hint").withColor(GOLD & 0x00FFFFFF));
        }
        if (e.done()) {
            lines.add(Component.translatable("fancy_journal.tooltip.done").withColor(DONE & 0x00FFFFFF));
        } else if (e.progress() != null && e.progress().hasProgress() && e.progress().getProgressText() != null) {
            lines.add(Component.translatable("fancy_journal.tooltip.progress", e.progress().getProgressText()).withColor(ACCENT & 0x00FFFFFF));
        }
        return lines;
    }
}
