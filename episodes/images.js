// images.js
const images = {};

// Función que importa todas las imágenes de la carpeta
function importAll(r) {
  r.keys().forEach((key) => {
    const name = key.replace('./', ''); // dejamos la extensión
    images[name] = r(key);
  });
}

// Importa automáticamente todas las imágenes .webp
importAll(require.context('./', false, /\.webp$/));

export default images;
