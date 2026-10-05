package dev.fancyvanilla.harness.mixin;

import dev.fancyvanilla.harness.Harness;

import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(Minecraft.class)
public abstract class HarnessMixin {
    @Inject(method = "tick()V", at = @At("TAIL"))
    private void fjHarness$tick(CallbackInfo ci) {
        Harness.tick((Minecraft) (Object) this);
    }
}
