export type RegisterPayload = {
  username: string;
  face_image: string; // dataURL base64
  dni?: string;
  email?: string;
};

export type LoginPayload = {
  face_image: string; // dataURL base64
};

const AUTH_API = (import.meta as any).env?.VITE_AUTH_API || 'https://prediccion-de-sismos-facial-v1.onrender.com';

export async function registerUser(data: RegisterPayload) {
  const form = new FormData();
  form.append('username', data.username);
  form.append('face_image', data.face_image);
  if (data.dni) form.append('dni', data.dni);
  if (data.email) form.append('email', data.email);

  const res = await fetch(`${AUTH_API}/auth/register`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const errorText = await res.text();
    console.error('Register error:', res.status, errorText);
    throw new Error(`Error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export async function loginFace(data: LoginPayload) {
  const form = new FormData();
  form.append('face_image', data.face_image);

  console.log('Attempting facial login to:', `${AUTH_API}/auth/login/face`);

  const res = await fetch(`${AUTH_API}/auth/login/face`, {
    method: 'POST',
    body: form,
  });
  
  if (!res.ok) {
    const errorText = await res.text();
    console.error('Login error:', res.status, errorText);
    throw new Error(`Error ${res.status}: ${errorText}`);
  }
  
  return res.json() as Promise<{ access_token: string; token_type: string }>;
}

export async function me(token: string) {
  const res = await fetch(`${AUTH_API}/auth/me?token=${encodeURIComponent(token)}`);
  if (!res.ok) {
    const errorText = await res.text();
    console.error('Me error:', res.status, errorText);
    throw new Error(`Error ${res.status}: ${errorText}`);
  }
  return res.json();
}
