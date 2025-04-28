#include "AudioPlay.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFilemanager.h"
#include "Sound/SoundWaveProcedural.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"
#include "Logging/LogMacros.h"

DEFINE_LOG_CATEGORY_STATIC(LogAudioPlay, Log, All);

void UAudioPlay::PlayAudio(const FString& FilePath, UObject* WorldContext)
{
    if (!WorldContext)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Invalid WorldContext"));
        return;
    }

    USoundWaveProcedural* SoundWave = LoadWavFile(FilePath);
    if (!SoundWave)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Failed to load WAV file"));
        return;
    }

    UAudioComponent* AudioComponent = UGameplayStatics::SpawnSound2D(WorldContext, SoundWave);
    if (!AudioComponent)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Failed to play sound"));
        return;
    }

    // Schedule file deletion after playback duration
    DeleteFileAfterPlayback(WorldContext, FilePath, SoundWave->Duration);
}

USoundWaveProcedural* UAudioPlay::LoadWavFile(const FString& FilePath)
{
    if (!FPaths::FileExists(FilePath))
    {
        UE_LOG(LogAudioPlay, Error, TEXT("WAV file not found: %s"), *FilePath);
        return nullptr;
    }

    TArray<uint8> RawFileData;
    if (!FFileHelper::LoadFileToArray(RawFileData, *FilePath))
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Failed to load WAV file: %s"), *FilePath);
        return nullptr;
    }

    if (RawFileData.Num() <= 44)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Invalid WAV file (too small): %s"), *FilePath);
        return nullptr;
    }

    USoundWaveProcedural* SoundWave = NewObject<USoundWaveProcedural>();
    if (!SoundWave)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Failed to create SoundWave"));
        return nullptr;
    }

    // Extract audio format information
    uint32 SampleRate = 44100;
    uint16 NumChannels = 2;
    uint16 BitsPerSample = 16;
    uint32 ByteRate = SampleRate * NumChannels * (BitsPerSample / 8);

    SoundWave->SetSampleRate(SampleRate);
    SoundWave->NumChannels = NumChannels;

    int32 DataSize = RawFileData.Num() - 44;
    if (DataSize % (BitsPerSample / 8) != 0)
    {
        int32 Padding = (BitsPerSample / 8) - (DataSize % (BitsPerSample / 8));
        RawFileData.SetNum(RawFileData.Num() + Padding, true);
        DataSize += Padding;
        UE_LOG(LogAudioPlay, Warning, TEXT("Padded WAV file to align buffer size: %d bytes"), Padding);
    }

    float Duration = (float)DataSize / (ByteRate);
    SoundWave->Duration = Duration;

    if (SoundWave->Duration <= 0)
    {
        UE_LOG(LogAudioPlay, Error, TEXT("Invalid WAV file: duration is zero."));
        return nullptr;
    }

    SoundWave->QueueAudio(RawFileData.GetData() + 44, DataSize);
    UE_LOG(LogAudioPlay, Log, TEXT("Successfully loaded WAV file: %s"), *FilePath);

    return SoundWave;
}

void UAudioPlay::DeleteFileAfterPlayback(UObject* WorldContext, FString FilePath, float Delay)
{
    if (!WorldContext || FilePath.IsEmpty() || Delay <= 0)
    {
        return;
    }

    FTimerHandle TimerHandle;
    WorldContext->GetWorld()->GetTimerManager().SetTimer(TimerHandle, [FilePath]()
        {
            if (FPaths::FileExists(FilePath))
            {
                IPlatformFile& FileManager = FPlatformFileManager::Get().GetPlatformFile();
                if (FileManager.DeleteFile(*FilePath))
                {
                    UE_LOG(LogAudioPlay, Log, TEXT("Deleted WAV file after playback: %s"), *FilePath);
                }
                else
                {
                    UE_LOG(LogAudioPlay, Warning, TEXT("Failed to delete WAV file: %s"), *FilePath);
                }
            }
        }, Delay, false);
}
