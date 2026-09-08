import LoginForm from '@/components/LoginForm';

export default function LoginPage() {
  return (
    <main 
      className="min-h-screen flex items-center justify-center relative bg-cover bg-center"
      style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069&auto=format&fit=crop")' }}
    >
      {/* Dark, slightly blurred overlay to ensure the white form pops */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0"></div>
      
      {/* The existing form, pulled to the foreground using z-index */}
      <div className="z-10 shadow-2xl rounded-lg">
        <LoginForm />
      </div>
    </main>
  );
}