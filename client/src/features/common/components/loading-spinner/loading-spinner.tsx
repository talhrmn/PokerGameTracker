import styles from "./styles.module.css";

const LoadingSpinner = ({ message }: { message: string }) => {
	return (
		<div className={styles.loadingContainer}>
			<div className={styles.loadingSpinner}></div>
			<p>{message}</p>
		</div>
	);
};

export default LoadingSpinner;
