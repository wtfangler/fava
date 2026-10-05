package dev.fancyvanilla.journal.mixin;

import dev.fancyvanilla.journal.FvLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.LoadingOverlay;
import net.minecraft.util.Util;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Paints the Fancy Vanilla backdrop over the game start-up (and resource reload) screen. Vanilla keeps running its own
 * logic (progress, fade, finish callback); this only draws on top, using the same fade timings.
 */
@Mixin(LoadingOverlay.class)
public abstract class LoadingOverlayMixin {
    @Shadow private float currentProgress;
    @Shadow private long fadeOutStart;
    @Shadow private long fadeInStart;
    @Shadow @org.spongepowered.asm.mixin.Final private boolean fadeIn;
    @Shadow @org.spongepowered.asm.mixin.Final private Minecraft minecraft;

    @Inject(method = "extractRenderState", at = @At("TAIL"))
    private void fancyJournal$brand(GuiGraphicsExtractor g, int mouseX, int mouseY, float partial, CallbackInfo ci) {
        long now = Util.getMillis();
        float alpha = 1f;
        if (fadeOutStart > -1L) alpha = 1f - Math.min(1f, (now - fadeOutStart) / 1000f);
        else if (fadeIn && fadeInStart > -1L) alpha = Math.min(1f, (now - fadeInStart) / 500f);
        FvLoader.draw(minecraft, g, g.guiWidth(), g.guiHeight(), alpha, currentProgress);
    }
}
