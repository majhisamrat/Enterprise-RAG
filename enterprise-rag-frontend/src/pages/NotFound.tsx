import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div className="login">
      <div className="login-card" style={{ textAlign: 'center' }}>
        <h1>404</h1>
        <p>The requested route does not exist.</p>
        <Link to="/" className="button" style={{ display: 'inline-grid', marginTop: '16px', textDecoration: 'none' }}>
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
