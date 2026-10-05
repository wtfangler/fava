package dev.fancyvanilla.journal.mixin;

import dev.fancyvanilla.journal.AdvancementUpdates;
import net.minecraft.client.multiplayer.ClientAdvancements;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(ClientAdvancements.class)
public abstract class ClientAdvancementsMixin implements AdvancementUpdates {
    @Unique private long fancyJournal$revision;

    @Inject(method = "update", at = @At("RETURN"))
    private void fancyJournal$updated(CallbackInfo ci) {
        fancyJournal$revision++;
    }

    @Override
    public long fancyJournal$revision() {
        return fancyJournal$revision;
    }
}
