from tensorflow.keras.applications import ResNet50V2
from tensorflow.keras.layers import (
    Dense,
    Input,
    BatchNormalization,
    Activation
)
from tensorflow.keras.regularizers import l2
from tensorflow.keras.models import Model
import os


def get_encoder(input_shape=(224, 224, 3), weights=None):
    # Returns a ResNet50 encoder without the classification head
    # The ResNet50's output undergoes average pooling, resulting in a 2048-d vector
    
    if weights == 'imagenet':
        print('Using ImageNet weights')
    
    encoder = ResNet50V2(
        include_top=False,
        input_shape=input_shape,
        weights=weights,
        pooling='avg'
    )
        
    return encoder


def get_classifier(config):
    # Outputs a 2048-d feature
    encoder = get_encoder(
        input_shape=config['image_shape'], 
        weights=config['encoder_weights_path']
    )
    encoder.trainable = config['encoder_trainable']

    # Create classifier by adding one FC layer on top of encoder
    inputs = Input(config['image_shape'])
    x = encoder(inputs)
    outputs = Dense(
        config['num_classes'], 
        activation='softmax', 
        kernel_initializer='he_normal'
    )(x)
    model = Model(inputs=inputs, outputs=outputs)

    return model


def projection_head(x, hidden_dim=2048, hidden_layers=3, weight_decay=5e-4):
    for i in range(hidden_layers):
        x = Dense(
            hidden_dim,
            name=f"projection_layer_{i}",
            kernel_regularizer=l2(weight_decay),
        )(x)
        x = BatchNormalization()(x)
        x = Activation("relu")(x)
    outputs = Dense(hidden_dim, name="projection_output")(x)
    return outputs


def get_barlow_encoder(input_shape=(224, 224, 3), hidden_dim=2048, hidden_layers=3, weights=None):
    encoder = get_encoder(input_shape=input_shape, weights=weights)

    inputs = Input(input_shape)
    x = encoder(inputs)
    outputs = projection_head(x, hidden_dim=hidden_dim, hidden_layers=hidden_layers)
    model = Model(inputs=inputs, outputs=outputs)

    return model
