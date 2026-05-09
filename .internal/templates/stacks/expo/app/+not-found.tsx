import { View, Text, StyleSheet } from 'react-native';
import { Link } from 'expo-router';
import { colors } from '@constants/colors';

export default function NotFoundScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Page not found</Text>
      <Link href="/" style={styles.link}>
        Go home
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  text: { fontSize: 18, color: colors.text },
  link: { fontSize: 16, color: colors.primary, marginTop: 16 },
});
