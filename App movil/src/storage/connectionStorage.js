import AsyncStorage from "@react-native-async-storage/async-storage";

const CONNECTION_KEY = "@simpsons-tv/connection";

export async function saveConnection(connection) {
  await AsyncStorage.setItem(CONNECTION_KEY, JSON.stringify(connection));
}

export async function loadConnection() {
  const raw = await AsyncStorage.getItem(CONNECTION_KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function clearConnection() {
  await AsyncStorage.removeItem(CONNECTION_KEY);
}
