import torch
import numpy as np


def saliency(prediction_logit, token_ids_tensor_one_hot, norm=True):
    # Back-propegate the gradient from the selected output-logit
    grad = torch.autograd.grad(prediction_logit, token_ids_tensor_one_hot)[0]

    # token_ids_tensor_one_hot.grad is the gradient propegated to ever embedding dimension of
    # the input tokens.
    if norm:  # norm calculates a scalar value (L2 Norm)
        token_importance_raw = torch.norm(grad, dim=1)
        # print('token_importance_raw', token_ids_tensor_one_hot.grad.shape,
        # np.count_nonzero(token_ids_tensor_one_hot.detach().numpy(), axis=1))

        # Normalize the values so they add up to 1
        token_importance = token_importance_raw / torch.sum(token_importance_raw)
    else:
        token_importance = torch.sum(grad, dim=1)  # Only one value, all others are zero

    return token_importance


def saliency_on_d_embeddings(prediction_logit, inputs_embeds, aggregation="L2"):
    inputs_embeds.retain_grad()

    # Back-propegate the gradient from the selected output-logit

    # inputs_embeds.grad
    # token_ids_tensor_one_hot.grad is the gradient propegated to ever embedding dimension of
    # the input tokens.
    if aggregation == "L2":  # norm calculates a scalar value (L2 Norm)
        token_importance_raw = torch.norm(inputs_embeds.grad, dim=1)
        # print('token_importance_raw', token_ids_tensor_one_hot.grad.shape,
        # np.count_nonzero(token_ids_tensor_one_hot.detach().numpy(), axis=1))

        # Normalize the values so they add up to 1
        token_importance = token_importance_raw / torch.sum(token_importance_raw)
    elif aggregation == "sum":
        token_importance_raw = torch.sum(inputs_embeds.grad, dim=1)
        token_importance = token_importance_raw  # Hmmm, how to normalize if it includes negative values
    elif aggregation == "mean":
        token_importance_raw = torch.mean(inputs_embeds.grad, dim=1)
        token_importance = token_importance_raw  # Hmmm, how to normalize if it includes negative values

    return token_importance


def gradient_x_inputs_attribution(prediction_logit, inputs_embeds):
    inputs_embeds.retain_grad()
    # back-prop gradient
    grad = torch.autograd.grad(prediction_logit, inputs_embeds)[0]

    # Grad X Input
    grad_x_input = grad * inputs_embeds

    # Turn into a scalar value for each input token by taking L2 norm
    feature_importance = torch.norm(grad_x_input, dim=1)

    # Normalize so we can show scores as percentages
    token_importance_normalized = feature_importance / torch.sum(feature_importance)

    return token_importance_normalized
