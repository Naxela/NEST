//! Rendering a scene with baked lightmaps.
mod datatypes;
mod nest;

use bevy::{picking::*, prelude::*};
use bevy_blendy_cameras::*;

fn main() {
    App::new()
        .insert_resource(datatypes::LoadingStages::default())
        .insert_resource(datatypes::LightmapRegistry::default())

        .add_plugins(DefaultPlugins)
        .add_plugins(BlendyCamerasPlugin)
        .add_plugins(MeshPickingPlugin)

        .add_systems(Startup, load_gltf)
        .add_systems(Update, spawn_gltf.after(load_gltf))
        .add_systems(Update, set_lightmap_registry.after(spawn_gltf))

        .add_systems(Update, make_pickable.after(spawn_gltf))

        .add_systems(Startup, setup)
        .add_systems(Update, add_lightmaps_to_meshes.after(set_lightmap_registry))

        .run();
}

fn setup(mut commands: Commands) {
    // Spawn just the camera, no scene here to avoid conflict
    commands.spawn((
        Camera3d::default(),
        Transform::from_translation(Vec3::new(0.0, 1.5, 5.0)),
        OrbitCameraController::default(),
    ));

    #[cfg(target_arch = "wasm32")]
    nest::nestlib::eval("
        document.querySelector('canvas').style.width='100vw';
        document.querySelector('canvas').style.height='100vh';
        document.querySelector('canvas').style.outline='none';
    ");

}

fn load_gltf(
    mut commands: Commands,
    mut loading_stages: ResMut<datatypes::LoadingStages>,
    asset_server: Res<AssetServer>,
) {
    if !loading_stages.gltf_load {
        // Load the scene handle directly
        let scene_handle: Handle<Scene> = asset_server.load("models/model.glb#Scene0");
        commands.insert_resource(datatypes::GLTFScene(scene_handle));

        loading_stages.gltf_load = true;
    }
}

/// System to spawn the GLTF scene once it's fully loaded.
fn spawn_gltf(
    mut commands: Commands,
    gltf_scene: Res<datatypes::GLTFScene>,
    scenes: Res<Assets<Scene>>,
    mut loading_stages: ResMut<datatypes::LoadingStages>,
) {
    // If we've initiated the load but haven't spawned yet
    if loading_stages.gltf_load && !loading_stages.gltf_spawned {
        // Check if the scene is fully loaded
        if scenes.get(&gltf_scene.0).is_some() {
            loading_stages.gltf_spawned = true;

            nest::nestlib::debugCall("Spawning GLTF");

            // Spawn the entity with the scene root, a default transform, and visibility
            commands.spawn((
                SceneRoot(gltf_scene.0.clone()),
                Transform::default(),
                Visibility::default(),
            ));

        }
    }
}



fn make_pickable(
    mut commands: Commands,
    loading_stages: Res<datatypes::LoadingStages>,
    mut run: Local<bool>,
    meshes: Query<(Entity, &Name, &Mesh3d)>,
) {

    if !loading_stages.lightmap_textures || *run {
        return;
    }

    for (entity, n, m) in meshes.iter() {
    
        println!("{:?} was selected!", n);
        commands.entity(entity).observe(abcd);

    }

    *run = true; // Mark initialization as complete

}

pub fn abcd(
    click: Trigger<Pointer<Click>>,
    query: Query<&Name>
){
    let name = query.get(click.entity()).unwrap();
    //println!("{} was clicked!", click.entity());
    println!("{} was clicked!", name);
    nest::nestlib::debugCall("The following was selected:");
    nest::nestlib::debugCall(name);
    nest::nestlib::debugAlert(name);
    //nest::nestlib::debugCall(&click.entity().to_string());
}

// System to apply lightmap textures
pub fn add_lightmaps_to_meshes(
    mut loading_stages: ResMut<datatypes::LoadingStages>,
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    query: Query<(Entity, &MeshMaterial3d<StandardMaterial>, &datatypes::LightmapInfo)>,
) {  
    if loading_stages.lightmap_registry && !loading_stages.lightmap_textures {

        nest::nestlib::debugCall("Adding lightmaps");

        for (entity, material, lightmap_info) in query.iter() {

            nest::nestlib::debugCall("I'm not getting anything here...");
            nest::nestlib::debugCall(&entity.to_string());
            nest::nestlib::debugCall(&lightmap_info.lightmap_name.to_string());

            if let Some(mat) = materials.get_mut(&material.0) {
                mat.lightmap_exposure = lightmap_info.exposure;
                mat.reflectance = 0.0;
            }

            commands.entity(entity).insert(bevy::pbr::Lightmap {
                image: asset_server.load(format!("lightmaps/{}.ktx2", lightmap_info.lightmap_name)),
                ..default()
            });

        }

        loading_stages.lightmap_textures = true;
    }
}

pub fn set_lightmap_registry(
    query: Query<(Entity, &Name, Option<&GltfExtras>)>,
    mut commands: Commands,
    mut loading_stages: ResMut<datatypes::LoadingStages>,
    children_query: Query<&Children>,
    name_query: Query<&Name>,
) {
    if loading_stages.gltf_spawned && !loading_stages.lightmap_registry {
        if query.is_empty() {
            return;
        }

        nest::nestlib::debugCall("Creating lightmap registry");

        for (entity, name, extras) in query.iter() {
            let mut lightmap_found = false;
            let mut lightmap_name = String::new();

            // If there's any extras at all
            if let Some(extras) = extras {
                match serde_json::from_str::<datatypes::GltfExtrasValue>(&extras.value) {
                    Ok(parsed) => {
                        if let Some(lightmap) = parsed.tlm_lightmap {
                            lightmap_name = lightmap.to_string();
                            nest::nestlib::debugCall(&format!("Found lightmap:{}", lightmap_name));
                            lightmap_found = true;
                        }
                    }
                    Err(err) => {
                        println!("Failed to parse extras for {}: {}", name.as_str(), err);
                    }
                }
            }

            if lightmap_found {
                if let Ok(children) = children_query.get(entity) {
                    for child in children.iter() {
                        if let Ok(child_name) = name_query.get(*child) {
                            commands.entity(*child).insert(datatypes::LightmapInfo {

                                lightmap_name: lightmap_name.clone(),
                                exposure: 1000.0, // Default exposure value
                            });
                            nest::nestlib::debugCall(&format!("Inserting lightmap:{} for object: {}", lightmap_name, child_name));
                        }
                    }
                }
            }
        }

        loading_stages.lightmap_registry = true;
    }
}