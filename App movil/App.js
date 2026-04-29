import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ConnectScreen from "./src/screens/ConnectScreen";
import LibrariesScreen from "./src/screens/LibrariesScreen";
import SeasonsScreen from "./src/screens/SeasonsScreen";
import EpisodesScreen from "./src/screens/EpisodesScreen";
import EpisodeDetailScreen from "./src/screens/EpisodeDetailScreen";
import { palette } from "./src/theme/palette";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Connect"
        screenOptions={{
          headerStyle: { backgroundColor: palette.card },
          headerTintColor: palette.text,
          headerTitleStyle: { fontWeight: "700" },
          contentStyle: { backgroundColor: palette.background },
        }}
      >
        <Stack.Screen
          name="Connect"
          component={ConnectScreen}
          options={{ title: "Conectar Raspberry" }}
        />
        <Stack.Screen
          name="Libraries"
          component={LibrariesScreen}
          options={{ title: "Bibliotecas" }}
        />
        <Stack.Screen
          name="Seasons"
          component={SeasonsScreen}
          options={({ route }) => ({ title: route.params?.libraryName || "Temporadas" })}
        />
        <Stack.Screen
          name="Episodes"
          component={EpisodesScreen}
          options={({ route }) => ({
            title: route.params?.seasonTitle || "Episodios",
          })}
        />
        <Stack.Screen
          name="EpisodeDetail"
          component={EpisodeDetailScreen}
          options={({ route }) => ({
            title: route.params?.episode?.title || "Episodio",
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
