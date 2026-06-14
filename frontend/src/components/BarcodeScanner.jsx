import { useEffect, useRef } from 'react';
import { BrowserMultiFormatReader } from '@zxing/browser';

const BarcodeScanner = ({ active, onDetected, onError }) => {
    const videoRef = useRef(null);
    const readerRef = useRef(null);
    const onDetectedRef = useRef(onDetected);
    const onErrorRef = useRef(onError);

    useEffect(() => {
        onDetectedRef.current = onDetected;
        onErrorRef.current = onError;
    }, [onDetected, onError]);

    useEffect(() => {
        if (!active) {
            readerRef.current?.reset();
            readerRef.current = null;
            return undefined;
        }

        const reader = new BrowserMultiFormatReader();
        readerRef.current = reader;

        reader
            .decodeFromVideoDevice(undefined, videoRef.current, (result, error) => {
                if (result) {
                    onDetectedRef.current?.(result.getText());
                    reader.reset();
                    readerRef.current = null;
                } else if (error && error.name !== 'NotFoundException') {
                    onErrorRef.current?.('Unable to access camera. Check permissions or enter the barcode manually.');
                }
            })
            .catch(() => {
                onErrorRef.current?.('Camera access denied or unavailable. Enter the barcode manually.');
            });

        return () => {
            reader.reset();
            readerRef.current = null;
        };
    }, [active]);

    return (
        <div className="aspect-video bg-black/40 rounded-2xl overflow-hidden border border-white/10">
            <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
        </div>
    );
};

export default BarcodeScanner;
