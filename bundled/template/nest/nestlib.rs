use wasm_bindgen::prelude::*;
use bevy::utils::tracing::info;


pub fn debugCall(call:&str){
    #[cfg(target_arch = "wasm32")]
    info!("{}",call.to_string());
    
    println!("{}",call.to_string());
}

pub fn debugUnknown(call:Option<&bevy::gltf::GltfExtras>){ //Todo, make agnotistic
    #[cfg(target_arch = "wasm32")]
    info!("{:?}",call);
    
    println!("{:?}",call);
}

pub fn debugAlert(call:&str){
    #[cfg(target_arch = "wasm32")]
    eval(&format!("alert('{}')", call));

    //nest::nestlib::debugCall(&format!("Found lightmap:{}", lightmap_name));
}



#[wasm_bindgen]
extern "C" {
    // Bind the global `eval` function
    #[wasm_bindgen(js_namespace = globalThis)]
    pub fn eval(js_code: &str) -> JsValue;
}