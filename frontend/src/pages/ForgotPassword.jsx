import React from 'react';

import { Leaf } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ForgotPassword() {
  return (
    <div className="min-h-screen hero-gradient flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm surface-card rounded-[32px] p-7">
        <div className="flex flex-col items-center mb-7">
          <div className="w-16 h-16 rounded-3xl bg-[#12523A] flex items-center justify-center mb-3 shadow-[0_10px_24px_-8px_rgba(18,82,58,0.55)]">
            <Leaf className="w-8 h-8 text-[#9CF7C4]" />
          </div>
          <h1 className="font-heading text-2xl font-extrabold text-[#10221A]">Mot de passe oublié</h1>
          <p className="text-sm text-[#8A9A91] font-body mt-1">
            La récupération du mot de passe par email n’est pas encore disponible.
          </p>
        </div>

        <div className="text-center">
          <Link to="/login" className="text-sm text-[#8A9A91] font-body hover:underline">
            Retour à la connexion
          </Link>
        </div>
      </div>
    </div>
  );
}
