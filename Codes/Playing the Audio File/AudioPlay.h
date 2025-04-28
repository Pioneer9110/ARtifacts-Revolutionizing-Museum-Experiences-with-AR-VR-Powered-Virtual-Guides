#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Sound/SoundWaveProcedural.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "AudioPlay.generated.h"

UCLASS()
class FINAL_P_API UAudioPlay : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Audio")
    static void PlayAudio(const FString& FilePath, UObject* WorldContext);

private:
    static USoundWaveProcedural* LoadWavFile(const FString& FilePath);
    static void DeleteFileAfterPlayback(UObject* WorldContext, FString FilePath, float Delay);
};
