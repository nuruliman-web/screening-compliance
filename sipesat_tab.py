import streamlit as st
import pandas as pd
import io

def run_sipesat():
    st.markdown("### 📋 Pengolahan & Rekap Data SIPESAT")
    st.write("Upload file mentah nasabah (Excel atau CSV) untuk diolah otomatis menjadi format standar SIPESAT.")

    uploaded_file = st.file_uploader(
        "Pilih file mentah data nasabah", 
        type=["xlsx", "xls", "csv"], 
        key="sipesat_uploader"
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file, dtype=str)
            else:
                df_raw = pd.read_excel(uploaded_file, dtype=str)
            
            with st.expander("📋 Preview Data Mentah (5 Baris Pertama)"):
                st.dataframe(df_raw.head())

            st.info("⚙️ Sedang menyelaraskan kolom dan membersihkan data...")
            
            target_columns = [
                'IDPJK', 'kodenasabah', 'namanasabah', 'tempatLahir', 
                'TanggalLahir', 'Alamat', 'No.KTP', 'No.Idlain', 'No.CIF', 'No.NPWP'
            ]
            
            df_processed = pd.DataFrame(columns=target_columns)
            
            for col in target_columns:
                matched_col = [c for c in df_raw.columns if c.lower().strip().replace(" ", "") == col.lower().strip().replace(" ", "")]
                if matched_col:
                    df_processed[col] = df_raw[matched_col[0]]
                else:
                    df_processed[col] = ""

            for text_upper_col in ['namanasabah', 'tempatLahir', 'Alamat']:
                if text_upper_col in df_processed.columns:
                    df_processed[text_upper_col] = df_processed[text_upper_col].fillna("").astype(str).str.upper().str.strip()

            for num_col in ['IDPJK', 'kodenasabah', 'No.KTP', 'No.Idlain', 'No.CIF', 'No.NPWP']:
                if num_col in df_processed.columns:
                    df_processed[num_col] = df_processed[num_col].fillna("").astype(str).apply(
                        lambda x: x.split('.')[0] if x.endswith('.0') else x
                    ).str.strip()

            st.subheader("✨ Hasil Standar Data SIPESAT")
            st.dataframe(df_processed, hide_index=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_processed.to_excel(writer, index=False, sheet_name='SIPESAT_RECAP')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Hasil Rekap SIPESAT (Excel)",
                data=processed_data,
                file_name="Hasil_Rekap_SIPESAT.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.success("Data berhasil diproses! Silakan unduh file Excel di atas.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
