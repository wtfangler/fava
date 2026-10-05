package dev.fancyvanilla.journal;

import com.mojang.blaze3d.platform.NativeImage;
import java.io.InputStream;
import java.nio.file.Files;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Util;

/**
 * Fancy Vanilla loading backdrop: charcoal background, the wordmark and a thin progress line.
 * The logo is read straight from the mod jar and registered as a dynamic texture, because at the first
 * resource reload the mod's own resource pack is not yet available to the texture manager.
 * If anything fails the backdrop is simply skipped and vanilla's screen stays visible.
 */
public final class FvLoader {
    private static final Identifier LOGO = Identifier.parse("fancy_journal:loader_logo");
    private static final int BG = 0x0E1013, TRACK = 0x262B33, ACCENT = 0x8FB4E8;
    private static int logoW, logoH;
    private static boolean tried, ready;

    private FvLoader() { }

    private static void ensureLogo(Minecraft mc) {
        if (tried) return;
        tried = true;
        try {
            var path = FabricLoader.getInstance().getModContainer("fancy_journal").orElseThrow()
                    .findPath("assets/fancy_journal/loader/logo.png").orElseThrow();
            try (InputStream in = Files.newInputStream(path)) {
                NativeImage image = NativeImage.read(in);
                logoW = image.getWidth();
                logoH = image.getHeight();
                mc.getTextureManager().register(LOGO, new DynamicTexture(() -> "fancy_journal loader logo", image));
                ready = true;
            }
        } catch (Throwable t) {
            ready = false;
        }
    }

    private static int argb(int rgb, float alpha) {
        int a = Math.max(0, Math.min(255, Math.round(alpha * 255f)));
        return (a << 24) | rgb;
    }

    /** @param progress 0..1, or a negative value for an endless sweeping bar. */
    public static void draw(Minecraft mc, GuiGraphicsExtractor g, int w, int h, float alpha, float progress) {
        ensureLogo(mc);
        if (!ready || alpha <= 0.003f) return;
        g.fill(0, 0, w, h, argb(BG, alpha));
        double scale = Math.max(1.0, mc.getWindow().getGuiScale());
        // 1 texel = 1 device pixel at any GUI scale, so the wordmark stays sharp; shrink only if the window is tiny
        int dw = (int) Math.round(logoW / scale), dh = (int) Math.round(logoH / scale);
        if (dw > w * 0.7) { dh = (int) (dh * (w * 0.7) / dw); dw = (int) (w * 0.7); }
        boolean message = progress < 0f; // message screens draw their text at the centre: logo goes above it, the bar below
        int x = (w - dw) / 2, y = message ? h / 2 - dh - 22 : h / 2 - dh;
        g.blit(RenderPipelines.GUI_TEXTURED, LOGO, x, y, 0f, 0f, dw, dh, logoW, logoH, logoW, logoH, argb(0xFFFFFF, alpha));
        int barW = Math.min(dw, 260), barH = 2, bx = (w - barW) / 2, by = message ? h / 2 + 46 : y + dh + Math.max(14, h / 24);
        g.fill(bx, by, bx + barW, by + barH, argb(TRACK, alpha));
        if (progress >= 0f) {
            int fillW = Math.round(barW * Math.max(0f, Math.min(1f, progress)));
            if (fillW > 0) g.fill(bx, by, bx + fillW, by + barH, argb(ACCENT, alpha));
        } else {
            double t = (Util.getMillis() % 1400L) / 1400.0;
            int seg = barW / 4, start = (int) (-seg + t * (barW + seg));
            int s0 = Math.max(0, start), s1 = Math.min(barW, start + seg);
            if (s1 > s0) g.fill(bx + s0, by, bx + s1, by + barH, argb(ACCENT, alpha));
        }
    }
}
