import infoCaps from "./Info.Caps";
import images from "../../../episodes/images";

function padEpisodeNumber(value) {
  return String(value || "").padStart(2, "0");
}

function normalizeEpisodeId(value) {
  return String(value || "").trim().toLowerCase();
}

function buildEpisodeKey(seasonNumber, episodeNumber) {
  if (!seasonNumber || !episodeNumber) {
    return "";
  }

  return `${Number(seasonNumber)}x${padEpisodeNumber(episodeNumber)}`;
}

const metadataByKey = new Map();

for (const season of infoCaps.seasons || []) {
  for (const episode of season.episodes || []) {
    const keyFromNumbers = buildEpisodeKey(season.id, episode.episodeNumber);
    const normalizedId = normalizeEpisodeId(episode.id);
    const payload = {
      ...episode,
      seasonNumber: season.id,
      seasonTitle: season.title,
    };

    if (keyFromNumbers) {
      metadataByKey.set(keyFromNumbers, payload);
    }

    if (normalizedId) {
      metadataByKey.set(normalizedId, payload);
    }
  }
}

function resolveImageSource(metadata, seasonNumber, episodeNumber) {
  const candidates = [];

  if (metadata?.image) {
    candidates.push(metadata.image.replace(/\.[^.]+$/, ".webp"));
  }

  const paddedKey = buildEpisodeKey(seasonNumber, episodeNumber);
  if (paddedKey) {
    candidates.push(`${paddedKey}.webp`);
  }

  if (seasonNumber && episodeNumber) {
    candidates.push(`${Number(seasonNumber)}x${Number(episodeNumber)}.webp`);
  }

  for (const candidate of candidates) {
    if (candidate && images[candidate]) {
      return images[candidate];
    }
  }

  return null;
}

export function getEpisodeMetadata(serverEpisode) {
  const normalizedId = normalizeEpisodeId(serverEpisode?.id);
  const keyFromNumbers = buildEpisodeKey(
    serverEpisode?.seasonNumber,
    serverEpisode?.episodeNumber
  );

  return metadataByKey.get(keyFromNumbers) || metadataByKey.get(normalizedId) || null;
}

export function buildClientEpisode(serverEpisode, libraryName) {
  const metadata = getEpisodeMetadata(serverEpisode);
  const imageSource = resolveImageSource(
    metadata,
    serverEpisode?.seasonNumber,
    serverEpisode?.episodeNumber
  );

  return {
    id: serverEpisode.id,
    title:
      metadata?.title ||
      `Episodio ${String(serverEpisode?.episodeNumber || "").padStart(2, "0")}`,
    synopsis:
      metadata?.synopsis ||
      `Archivo detectado en ${libraryName}. Ruta: ${serverEpisode.relativePath}`,
    seasonNumber: serverEpisode.seasonNumber,
    episodeNumber: serverEpisode.episodeNumber,
    directoryPath: serverEpisode.relativePath,
    file: serverEpisode.file,
    imageSource,
  };
}
