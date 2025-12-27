namespace RolePlayClient.Models;

public record GameState(Scene Scene, Dictionary<string, Character> Characters);

public record Scene(
    string Location,
    string Time,
    string Description,
    List<InteractiveObject> InteractiveObjects
);

public record InteractiveObject(string Name, string Location, string State);

public record Character(
    int Age,
    string Description,
    string Personality,
    string CurrentAction,
    List<string> CurrentEmotion,
    string Goal,
    List<string> Knowledge,
    List<Relationship> Relationships,
    string LocationInScene,
    Clothing Clothing,
    List<string> Inventory,
    List<string> Holding
);

public record Relationship(string Target, string Type);

public record Clothing(
    List<string> Head,
    List<string> Face,
    List<string> Underwear,
    List<string> Torso,
    List<string> Body,
    List<string> Overwear,
    List<string> Legs,
    List<string> Feet,
    List<string> Hands
);
