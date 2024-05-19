import { AppProps } from "next/app";
import store from "../redux/store";
import { Provider } from "react-redux";

const App = ({ Component, pageProps }: AppProps) => {
  return <Component {...pageProps} />;
};

export default function AppWrapper(props: AppProps) {
  return (
    <Provider store={store}>
      <App {...props} />
    </Provider>
  );
}
