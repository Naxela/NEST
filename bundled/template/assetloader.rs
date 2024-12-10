use crate::datatypes;
use bevy::prelude::*;
use bevy_mod_picking::prelude::*;

pub fn load_gltf(
    mut commands: Commands,
    mut loading_stages: ResMut<datatypes::LoadingStages>,
    asset_server: Res<AssetServer>
) {
    if !loading_stages.gltf_load {

        //TODO - Observer (15?) or eventReader::sceneReady (14?)

        let gltf: Handle<Gltf> = asset_server.load("models/model.glb");
        commands.insert_resource(datatypes::GLTFScene(gltf));

        loading_stages.gltf_load = true; // Update the stage to mark as loaded
    }
}

pub fn spawn_gltf(
    mut commands: Commands,
    gltf_scene: Res<datatypes::GLTFScene>,
    gltf_assets: Res<Assets<Gltf>>,
    mut loading_stages: ResMut<datatypes::LoadingStages>,
) {
    // Check if GLTF is loaded but not yet spawned
    if loading_stages.gltf_load && !loading_stages.gltf_spawned {
        // Wait until the GLTF asset is loaded
        if let Some(gltf) = gltf_assets.get(&gltf_scene.0) {
            loading_stages.gltf_spawned = true; // Mark as spawned

            // Spawn the GLTF scene
            // commands.spawn(SceneBundle {
            //     scene: gltf.scenes[0].clone(),
            //     ..Default::default()
            // });

            commands.spawn((
                SceneBundle {
                    scene: gltf.scenes[0].clone(),
                    ..default()
                },
                // Events that target children of the scene will bubble up to this level and will fire off a
                // `HelmetClicked` event.
                On::<Pointer<Click>>::run(|event: Listener<Pointer<Click>>| {
                    info!("Clicked on entity {:?}", event.target);
                }),
            ));





        }
    }
}

// System to load audio
pub fn load_audio(mut loading_stages: ResMut<datatypes::LoadingStages>) {
    if loading_stages.lightmap_textures && !loading_stages.audio {
        loading_stages.audio = true;
    }
}