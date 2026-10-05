package dev.fancyvanilla.journal;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.loader.api.ModContainer;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.advancements.CriterionProgress;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.locale.Language;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.stats.StatsCounter;
import net.minecraft.stats.Stats;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * What a TEMPERED quest asks for, as a checklist: "Get: Copper ingot 5/8", "Mine: Stone 20/64", "Place: Bed".
 * <ul>
 * <li>The original quests are granted by functions, so their goals come from assets/tempered/quest_specs.json,
 *     generated at build time from those functions (tools/gen_quest_specs.py).</li>
 * <li>Personal quests are ordinary advancements: their criteria are read from the quest JSON in the mod jar
 *     (the client does not receive criteria conditions from the server).</li>
 * </ul>
 * Items are counted from the inventory, the rest from the player's statistics. Quests of other mods, or a client
 * without the data, have no spec and the HUD falls back to the description.
 */
final class QuestSpec {
    enum Kind { HAVE, PLACE, EAT, TAME, BREED, KILL, SUMMON, BUCKET, BREW, CRAFT, VISIT, FISH, MINE, USE, BREAK, STAT, GENERIC }

    /** ids are items/blocks/entities, or statistic keys for STAT (their values are added up). */
    record Target(Kind kind, List<String> ids, int count) { }

    /** One way to satisfy a requirement group; all its targets must hold. criterion is null for the original quests. */
    record Option(String criterion, List<Target> targets) { }

    /** Requirement group: any one of its options is enough. All groups are needed for the quest. */
    record Group(List<Option> anyOf) { }

    /** A line of the checklist as shown in the HUD. */
    record Line(Component text, int have, int need, boolean done) { }

    private static final Map<String, QuestSpec> CACHE = new HashMap<>();
    private static final Map<String, JsonObject> BAKED = new HashMap<>();
    private static final QuestSpec NONE = new QuestSpec(List.of());

    final List<Group> groups;

    private QuestSpec(List<Group> groups) {
        this.groups = groups;
    }

    /** The spec for an advancement id, or null when none can be read. */
    static synchronized QuestSpec of(String id) {
        QuestSpec spec = CACHE.computeIfAbsent(id, QuestSpec::load);
        return spec == NONE ? null : spec;
    }

    /** True when some line is counted from statistics, so the HUD should ask the server for them now and then. */
    boolean usesStats() {
        return groups.stream().flatMap(g -> g.anyOf().stream()).flatMap(o -> o.targets().stream()).anyMatch(t -> t.kind() == Kind.STAT);
    }

    private static QuestSpec load(String id) {
        try {
            Identifier identifier = Identifier.parse(id);
            var found = FabricLoader.getInstance().getModContainer(identifier.getNamespace());
            if (found.isEmpty()) return NONE;
            ModContainer container = found.get();
            JsonObject baked = baked(container, identifier.getNamespace());
            if (baked != null && baked.has(id)) return fromBaked(baked.getAsJsonObject(id));
            var path = container.findPath("data/" + identifier.getNamespace() + "/advancement/" + identifier.getPath() + ".json");
            if (path.isEmpty()) return NONE;
            return parse(JsonParser.parseString(Files.readString(path.get(), StandardCharsets.UTF_8)).getAsJsonObject());
        } catch (IOException | RuntimeException e) {
            Journal.LOGGER.debug("No quest spec for {}", id, e);
            return NONE;
        }
    }

    private static JsonObject baked(ModContainer container, String namespace) throws IOException {
        if (BAKED.containsKey(namespace)) return BAKED.get(namespace);
        JsonObject specs = null;
        var path = container.findPath("assets/" + namespace + "/quest_specs.json");
        if (path.isPresent()) {
            specs = JsonParser.parseString(Files.readString(path.get(), StandardCharsets.UTF_8)).getAsJsonObject();
        }
        BAKED.put(namespace, specs);
        return specs;
    }

    private static QuestSpec fromBaked(JsonObject spec) {
        List<Group> groups = new ArrayList<>();
        for (JsonElement element : spec.getAsJsonArray("reqs")) {
            JsonObject req = element.getAsJsonObject();
            String kind = req.get("kind").getAsString();
            int need = req.has("need") ? req.get("need").getAsInt() : 1;
            Target target = switch (kind) {
                case "have" -> new Target(Kind.HAVE, ids(req.get("ids")), need);
                case "stat" -> new Target(Kind.STAT, ids(req.get("stats")), need);
                case "dimension" -> new Target(Kind.VISIT, ids(req.get("id")), 1);
                default -> null;
            };
            if (target != null && !target.ids().isEmpty()) groups.add(new Group(List.of(new Option(null, List.of(target)))));
        }
        return groups.isEmpty() ? NONE : new QuestSpec(groups);
    }

    private static QuestSpec parse(JsonObject root) {
        JsonObject criteria = root.getAsJsonObject("criteria");
        Map<String, Option> options = new HashMap<>();
        boolean onlyImpossible = true;
        for (var entry : criteria.entrySet()) {
            JsonObject criterion = entry.getValue().getAsJsonObject();
            String trigger = criterion.has("trigger") ? criterion.get("trigger").getAsString() : "";
            if (!trigger.equals("minecraft:impossible")) onlyImpossible = false;
            options.put(entry.getKey(), option(entry.getKey(), criterion));
        }
        if (onlyImpossible) return NONE;
        List<Group> groups = new ArrayList<>();
        if (root.has("requirements")) {
            for (JsonElement group : root.getAsJsonArray("requirements")) {
                List<Option> any = new ArrayList<>();
                for (JsonElement name : group.getAsJsonArray()) {
                    Option option = options.get(name.getAsString());
                    if (option != null) any.add(option);
                }
                if (!any.isEmpty()) groups.add(new Group(any));
            }
        } else {
            options.values().forEach(o -> groups.add(new Group(List.of(o))));
        }
        return groups.isEmpty() ? NONE : new QuestSpec(groups);
    }

    // ------------------------------------------------------------------ parsing the conditions

    private static Option option(String name, JsonObject criterion) {
        String trigger = criterion.has("trigger") ? criterion.get("trigger").getAsString() : "";
        JsonObject c = criterion.has("conditions") ? criterion.getAsJsonObject("conditions") : new JsonObject();
        List<Target> targets = new ArrayList<>();
        switch (trigger) {
            case "minecraft:inventory_changed" -> {
                for (JsonObject p : terms(c.get("items"))) {
                    targets.add(new Target(Kind.HAVE, ids(p.get("items")), minCount(p.get("count"))));
                }
            }
            case "minecraft:placed_block" -> targets.add(new Target(Kind.PLACE, locationBlocks(c), 1));
            case "minecraft:consume_item" -> targets.add(new Target(Kind.EAT, itemIds(c, "item"), 1));
            case "minecraft:filled_bucket" -> targets.add(new Target(Kind.BUCKET, itemIds(c, "item"), 1));
            case "minecraft:fishing_rod_hooked" -> targets.add(new Target(Kind.FISH, itemIds(c, "item"), 1));
            case "minecraft:tame_animal" -> targets.add(new Target(Kind.TAME, entityTypes(c, "entity"), 1));
            case "minecraft:summoned_entity" -> targets.add(new Target(Kind.SUMMON, entityTypes(c, "entity"), 1));
            case "minecraft:player_killed_entity" -> targets.add(new Target(Kind.KILL, entityTypes(c, "entity"), 1));
            case "minecraft:bred_animals" -> targets.add(new Target(Kind.BREED, entityTypes(c, "child"), 1));
            case "minecraft:brewed_potion" -> targets.add(new Target(Kind.BREW, ids(c.get("potion")), 1));
            case "minecraft:recipe_crafted" -> targets.add(new Target(Kind.CRAFT, ids(c.get("recipe_id")), 1));
            case "minecraft:location" -> targets.add(new Target(Kind.VISIT, structures(c), 1));
            default -> { }
        }
        targets.removeIf(t -> t.ids().isEmpty());
        if (targets.isEmpty()) targets.add(new Target(Kind.GENERIC, List.of(name), 1));
        return new Option(name, targets);
    }

    private static List<String> ids(JsonElement element) {
        List<String> out = new ArrayList<>();
        if (element == null || element.isJsonNull()) return out;
        if (element.isJsonArray()) {
            for (JsonElement e : element.getAsJsonArray()) out.addAll(ids(e));
        } else if (element.isJsonPrimitive()) {
            out.add(element.getAsString());
        } else if (element.isJsonObject() && element.getAsJsonObject().has("items")) {
            out.addAll(ids(element.getAsJsonObject().get("items")));
        }
        return out;
    }

    private static int minCount(JsonElement count) {
        if (count == null || count.isJsonNull()) return 1;
        if (count.isJsonPrimitive()) return Math.max(1, count.getAsInt());
        JsonObject o = count.getAsJsonObject();
        return o.has("min") ? Math.max(1, (int) Math.ceil(o.get("min").getAsDouble())) : 1;
    }

    private static List<String> itemIds(JsonObject c, String field) {
        return c.has(field) && c.get(field).isJsonObject() ? ids(c.getAsJsonObject(field).get("items")) : List.of();
    }

    /** Predicate terms of a condition field: a list in 26.2/1.21.x, a single object (or all_of) in 26.3. */
    private static List<JsonObject> terms(JsonElement element) {
        List<JsonObject> out = new ArrayList<>();
        if (element == null || element.isJsonNull()) return out;
        if (element.isJsonArray()) {
            for (JsonElement e : element.getAsJsonArray()) out.addAll(terms(e));
        } else if (element.isJsonObject()) {
            JsonObject o = element.getAsJsonObject();
            if (o.has("terms")) {
                out.addAll(terms(o.get("terms")));
            } else {
                out.add(o);
            }
        }
        return out;
    }

    private static JsonObject predicateOf(JsonObject term) {
        return term.has("predicate") && term.get("predicate").isJsonObject() ? term.getAsJsonObject("predicate") : null;
    }

    private static List<String> locationBlocks(JsonObject c) {
        for (JsonObject term : terms(c.get("location"))) {
            JsonObject predicate = predicateOf(term);
            if (predicate != null && predicate.has("block") && predicate.get("block").isJsonObject()) {
                return ids(predicate.getAsJsonObject("block").get("blocks"));
            }
        }
        return List.of();
    }

    /** The entity type of an entity predicate: "minecraft:entity_type" in 26.x, "type" in 1.21.x. */
    private static List<String> entityTypes(JsonObject c, String field) {
        for (JsonObject term : terms(c.get(field))) {
            JsonObject predicate = predicateOf(term);
            if (predicate == null) continue;
            if (predicate.has("minecraft:entity_type")) return ids(predicate.get("minecraft:entity_type"));
            if (predicate.has("type")) return ids(predicate.get("type"));
        }
        return List.of();
    }

    /** Structure of a location predicate: "minecraft:location"/"structures" in 26.x, "location"/"structure" in 1.21.x. */
    private static List<String> structures(JsonObject c) {
        for (JsonObject term : terms(c.get("player"))) {
            JsonObject predicate = predicateOf(term);
            if (predicate == null) continue;
            JsonObject location = predicate.has("minecraft:location") ? predicate.getAsJsonObject("minecraft:location")
                    : predicate.has("location") && predicate.get("location").isJsonObject() ? predicate.getAsJsonObject("location") : null;
            if (location == null) continue;
            if (location.has("structures")) return ids(location.get("structures"));
            if (location.has("structure")) return ids(location.get("structure"));
        }
        return List.of();
    }

    // ------------------------------------------------------------------ checklist for the HUD

    /** The checklist lines for the current state of the quest. */
    List<Line> lines(AdvancementProgress progress, Minecraft mc) {
        boolean questDone = progress != null && progress.isDone();
        List<Line> lines = new ArrayList<>();
        for (Group group : groups) {
            Option best = group.anyOf().get(0);
            boolean done = false;
            for (Option option : group.anyOf()) {
                if (isDone(progress, option, questDone)) {
                    best = option;
                    done = true;
                    break;
                }
            }
            Component text;
            if (group.anyOf().size() == 1 || done) {
                text = describe(best);
            } else {
                text = Component.empty();
                for (int i = 0; i < group.anyOf().size(); i++) {
                    if (i > 0) text = text.copy().append(Component.literal(" / "));
                    text = text.copy().append(describe(group.anyOf().get(i)));
                }
            }
            int need = 0;
            int have = 0;
            Target counted = best.targets().size() == 1 ? best.targets().get(0) : null;
            if (counted != null && (counted.kind() == Kind.HAVE || counted.kind() == Kind.STAT)) {
                int scale = counted.kind() == Kind.STAT ? statScale(counted.ids().get(0)) : 1;
                need = Math.max(1, counted.count() / scale);
                int current = counted.kind() == Kind.HAVE ? countItems(mc, counted) : statSum(mc, counted) / scale;
                // lifetime statistics can be ahead of the quest's own counter (old worlds): never claim completion early
                have = done ? need : Math.min(counted.kind() == Kind.STAT ? need - 1 : need, current);
            }
            lines.add(new Line(text, have, need, done));
        }
        return lines;
    }

    private static boolean isDone(AdvancementProgress progress, Option option, boolean questDone) {
        if (option.criterion() == null) return questDone;
        if (progress == null) return false;
        CriterionProgress criterion = progress.getCriterion(option.criterion());
        return criterion != null && criterion.isDone();
    }

    private static Component describe(Option option) {
        Component out = Component.empty();
        for (int i = 0; i < option.targets().size(); i++) {
            if (i > 0) out = out.copy().append(Component.literal(" + "));
            out = out.copy().append(describe(option.targets().get(i)));
        }
        return out;
    }

    private static Component describe(Target target) {
        if (target.kind() == Kind.GENERIC) return Component.literal(pretty(target.ids().get(0)));
        if (target.kind() == Kind.STAT) {
            String key = target.ids().get(0);
            String type = statType(key);
            Identifier id = statId(key);
            Kind verb = switch (type) {
                case "crafted" -> Kind.CRAFT;
                case "mined" -> Kind.MINE;
                case "killed" -> Kind.KILL;
                case "used" -> Kind.USE;
                case "broken" -> Kind.BREAK;
                default -> null;
            };
            if (verb == null) { // "custom": the statistic's own name, e.g. "Distance Walked", "Animals Bred"
                String statKey = "stat." + id.getNamespace() + "." + id.getPath();
                return Language.getInstance().has(statKey) ? Component.translatable(statKey) : Component.literal(pretty(id.getPath()));
            }
            Component names = name(verb, id.toString());
            for (int i = 1; i < target.ids().size(); i++) {
                names = names.copy().append(Component.literal(" +" + (target.ids().size() - 1)));
                break;
            }
            return Component.translatable("fancy_journal.req." + verb.name().toLowerCase(Locale.ROOT), names);
        }
        Component names = name(target.kind(), target.ids().get(0));
        if (target.ids().size() > 1) names = names.copy().append(Component.literal(" +" + (target.ids().size() - 1)));
        return Component.translatable("fancy_journal.req." + target.kind().name().toLowerCase(Locale.ROOT), names);
    }

    static Component name(Kind kind, String id) {
        if (kind == Kind.GENERIC) return Component.literal(pretty(id));
        boolean tag = id.startsWith("#");
        Identifier identifier = Identifier.parse(tag ? id.substring(1) : id);
        String ns = identifier.getNamespace(), path = identifier.getPath();
        if (kind == Kind.VISIT && !tag) {
            String dimension = switch (path) {
                case "the_nether" -> "advancements.nether.root.title";
                case "the_end" -> "advancements.end.root.title";
                default -> null;
            };
            if (dimension != null && Language.getInstance().has(dimension)) return Component.translatable(dimension);
        }
        String[] keys;
        if (tag) {
            keys = new String[] {"fancy_journal.tag." + ns + "." + path, "tag.item." + ns + "." + path, "tag.block." + ns + "." + path};
        } else {
            keys = switch (kind) {
                case PLACE, MINE -> new String[] {"block." + ns + "." + path, "item." + ns + "." + path};
                case TAME, BREED, KILL, SUMMON -> new String[] {"entity." + ns + "." + path};
                case VISIT -> new String[] {"structure." + ns + "." + path};
                case CRAFT -> new String[] {"item." + ns + "." + path, "item." + ns + "." + path.replace("_smithing_trim", "")};
                default -> new String[] {"item." + ns + "." + path, "block." + ns + "." + path};
            };
        }
        for (String key : keys) {
            if (Language.getInstance().has(key)) return Component.translatable(key);
        }
        return Component.literal(pretty(path));
    }

    private static String pretty(String text) {
        String last = text.contains("/") ? text.substring(text.lastIndexOf('/') + 1) : text;
        last = last.replace('_', ' ').trim();
        return last.isEmpty() ? text : Character.toUpperCase(last.charAt(0)) + last.substring(1);
    }

    // ------------------------------------------------------------------ counting

    /** How many matching items the player carries right now (same count the quest itself uses). */
    private static int countItems(Minecraft mc, Target target) {
        if (mc.player == null) return 0;
        Inventory inventory = mc.player.getInventory();
        int total = 0;
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            ItemStack stack = inventory.getItem(slot);
            if (!stack.isEmpty() && matches(stack, target.ids())) total += stack.getCount();
        }
        return total;
    }

    private static boolean matches(ItemStack stack, List<String> ids) {
        for (String id : ids) {
            if (id.startsWith("#")) {
                TagKey<Item> tag = TagKey.create(Registries.ITEM, Identifier.parse(id.substring(1)));
                if (stack.is(holder -> holder.is(tag))) return true;
            } else if (BuiltInRegistries.ITEM.getKey(stack.getItem()).equals(Identifier.parse(id))) {
                return true;
            }
        }
        return false;
    }

    /** "minecraft.mined:minecraft.stone" -> "mined" */
    private static String statType(String key) {
        return key.substring(key.indexOf('.') + 1, key.indexOf(':'));
    }

    /** "minecraft.mined:minecraft.stone" -> minecraft:stone */
    private static Identifier statId(String key) {
        String id = key.substring(key.indexOf(':') + 1);
        int dot = id.indexOf('.');
        return Identifier.parse(dot < 0 ? id : id.substring(0, dot) + ":" + id.substring(dot + 1));
    }

    /** Distances are stored in centimetres and damage in tenths of a point; quests and descriptions use blocks and points. */
    private static int statScale(String key) {
        if (!statType(key).equals("custom")) return 1;
        String path = statId(key).getPath();
        if (path.endsWith("_one_cm")) return 100;
        if (path.startsWith("damage_")) return 10;
        return 1;
    }

    private static int statSum(Minecraft mc, Target target) {
        if (mc.player == null) return 0;
        StatsCounter stats = mc.player.getStats();
        long total = 0;
        for (String key : target.ids()) {
            Identifier id = statId(key);
            total += switch (statType(key)) {
                case "crafted" -> stats.getValue(Stats.ITEM_CRAFTED, BuiltInRegistries.ITEM.getValue(id));
                case "used" -> stats.getValue(Stats.ITEM_USED, BuiltInRegistries.ITEM.getValue(id));
                case "broken" -> stats.getValue(Stats.ITEM_BROKEN, BuiltInRegistries.ITEM.getValue(id));
                case "mined" -> stats.getValue(Stats.BLOCK_MINED, BuiltInRegistries.BLOCK.getValue(id));
                case "killed" -> stats.getValue(Stats.ENTITY_KILLED, BuiltInRegistries.ENTITY_TYPE.getValue(id));
                case "custom" -> stats.getValue(Stats.CUSTOM, id);
                default -> 0;
            };
        }
        return (int) Math.min(Integer.MAX_VALUE, total);
    }
}
